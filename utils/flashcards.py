# utils/flashcards.py
import json
import os
import re
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini

from core.settings import settings
from utils.logger import get_logger

load_dotenv()

logger = get_logger()


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
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            return {
                "flashcards": [],
                "error": "GEMINI_API_KEY environment variable not set",
            }

        # Initialize Gemini LLM
        llm = Gemini(api_key=gemini_api_key)
        logger.info("Gemini LLM initialized")

        # Read Markdown file using file_id
        markdown_path = Path(settings.OUTPUT_DIR) / f"{file_id}.md"
        if not markdown_path.exists():
            logger.error(
                "Markdown file not found", extra={"markdown_path": markdown_path}
            )
            return {
                "flashcards": [],
                "error": f"Markdown file not found: {markdown_path}",
            }

        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        logger.info("Markdown content loaded", extra={"markdown_path": markdown_path})

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

        cleaned_response = re.sub(
            r"^```json\s*|\s*```$", "", raw_response, flags=re.IGNORECASE | re.DOTALL
        ).strip()
        logger.info(
            "Cleaned response for JSON parsing",
            extra={"cleaned_response": cleaned_response},
        )

        # Attempt to parse JSON
        try:
            flashcards = json.loads(cleaned_response)
            if not isinstance(flashcards, list) or not all(
                isinstance(card, dict) for card in flashcards
            ):
                logger.error("Invalid flashcard format: not a list of dictionaries")
                return {"flashcards": [], "error": "Invalid flashcard format"}

            # Validate that each flashcard has 'question' and 'answer'
            validated_flashcards = []
            for card in flashcards:
                if "question" in card and "answer" in card:
                    validated_flashcards.append(
                        {"question": card["question"], "answer": card["answer"]}
                    )
                else:
                    logger.warning("Skipping malformed flashcard", extra={"card": card})

            logger.info(
                "Parsed and validated flashcards",
                extra={"flashcards": validated_flashcards},
            )

            # Save flashcards to JSON file (optional, but good for caching/debugging)
            flashcards_path = (
                Path(settings.OUTPUT_DIR) / f"flashcards_{file_id}_{language}.json"
            )  # Include language in filename
            with open(flashcards_path, "w", encoding="utf-8") as f:
                json.dump(validated_flashcards, f, indent=2)
            logger.info("Flashcards saved", extra={"flashcards_path": flashcards_path})

            return {"flashcards": validated_flashcards}
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON response after cleaning",
                extra={"cleaned_response": cleaned_response},
            )
            return {
                "flashcards": [],
                "error": f"Failed to parse LLM response: {str(e)}",
            }

    except Exception as e:
        logger.error("Error generating flashcards", extra={"error": str(e)})
        return {"flashcards": [], "error": f"Error generating flashcards: {str(e)}"}
