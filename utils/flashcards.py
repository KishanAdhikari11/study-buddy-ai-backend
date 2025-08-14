# utils/flashcards.py
from llama_index.llms.gemini import Gemini
from core.config import settings
from pathlib import Path
from typing import List, Dict
import json
import logging
import re
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def generate_flashcards(file_id: str, num_cards: int = 5, language: str = "en") -> Dict:
    """
    Generate flashcards from Markdown content stored in output_<file_id>.md
    Args:
        file_id (str): Unique identifier for the Markdown file
        num_cards (int): Number of flashcards to generate
        language (str): Desired language for the flashcards.
    Returns:
        Dict: Dictionary containing flashcards or error message
    """
    try:
        # Load Gemini API key
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            logger.error("GOOGLE_API_KEY environment variable not set")
            return {"flashcards": [], "error": "GOOGLE_API_KEY environment variable not set"}

        # Initialize Gemini LLM
        llm = Gemini(api_key=GEMINI_API_KEY)
        logger.info("Gemini LLM initialized")

        # Read Markdown file using file_id
        markdown_path = Path(settings.OUTPUT_DIR) / f"{file_id}.md"
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return {"flashcards": [], "error": f"Markdown file not found: {markdown_path}"}

        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        logger.info(f"Markdown content loaded from {markdown_path}")

        if not markdown_content.strip():
            logger.warning("Markdown content is empty")
            return {"flashcards": [], "error": "No content in Markdown file"}

        # Construct prompt with Markdown content, making language and number of cards dynamic
        prompt = f"""
        You are a flashcard generator. Using the following content extracted from a document, create exactly {num_cards} flashcards with concise question-answer pairs.
        The questions and answers should be strictly in {language}.
        Return the flashcards as a raw JSON array, ensuring valid JSON syntax, without wrapping it in code blocks (```json or ```) or adding any extra text, explanations, or comments.
        Each flashcard object should have a "question" key and an "answer" key.

        Example Format:
        [
            {{
                "question": "What is the capital of France?",
                "answer": "Paris"
            }},
            {{
                "question": "What is 2+2?",
                "answer": "4"
            }}
        ]

        If the content is insufficient to generate flashcards, return an empty array:

        []

        Content:
        {markdown_content}
        """

        # Query Gemini
        response = llm.complete(prompt)
        raw_response = response.text
        logger.info(f"Raw LLM response: {raw_response}")

        # Clean response: remove Markdown code block markers and extra whitespace
        cleaned_response = re.sub(r'^```json\s*|\s*```$', '', raw_response, flags=re.IGNORECASE|re.DOTALL).strip()
        logger.info(f"Cleaned response for JSON parsing: {cleaned_response}")

        # Attempt to parse JSON
        try:
            flashcards = json.loads(cleaned_response)
            if not isinstance(flashcards, list) or not all(isinstance(card, dict) for card in flashcards):
                logger.error("Invalid flashcard format: not a list of dictionaries")
                return {"flashcards": [], "error": "Invalid flashcard format"}
            
            # Validate that each flashcard has 'question' and 'answer'
            validated_flashcards = []
            for card in flashcards:
                if "question" in card and "answer" in card:
                    validated_flashcards.append({
                        "question": card["question"],
                        "answer": card["answer"]
                    })
                else:
                    logger.warning(f"Skipping malformed flashcard: {card}. Missing 'question' or 'answer'.")
            
            logger.info(f"Parsed and validated flashcards: {validated_flashcards}")

            # Save flashcards to JSON file (optional, but good for caching/debugging)
            flashcards_path = Path(settings.OUTPUT_DIR) / f"flashcards_{file_id}_{language}.json" # Include language in filename
            with open(flashcards_path, "w", encoding="utf-8") as f:
                json.dump(validated_flashcards, f, indent=2)
            logger.info(f"Flashcards saved to {flashcards_path}")

            return {"flashcards": validated_flashcards}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response after cleaning: {cleaned_response}")
            return {"flashcards": [], "error": f"Failed to parse LLM response: {str(e)}"}

    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        return {"flashcards": [], "error": f"Error generating flashcards: {str(e)}"}