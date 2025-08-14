from llama_index.llms.gemini import Gemini
from pathlib import Path
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pydantic_settings import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "study-buddy"
    UPLOAD_DIR: str = str(Path("static/uploads"))
    OUTPUT_DIR: str = str(Path("static/outputs"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
def test_gemini(file_id: str, num_questions: int):
    try:
        # Initialize Gemini LLM
        llm = Gemini(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini LLM initialized")

        # Read Markdown file using file_id
        markdown_path = Path(settings.OUTPUT_DIR) / "output.md"
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return {"questions": [], "error": f"Markdown file not found: {markdown_path}"}

        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        logger.info(f"Markdown content loaded from {markdown_path}")

        if not markdown_content.strip():
            logger.warning("Markdown content is empty")
            return {"questions": [], "error": "No content in Markdown file"}

        # Construct prompt with Markdown content
        prompt = f"""
        You are a quiz generator. Using the following content extracted from a PDF, create a quiz with exactly {num_questions} multiple-choice questions. Each question must have exactly 4 answer options, with one correct answer clearly indicated. Return the quiz as a raw JSON object, ensuring valid JSON syntax, without wrapping it in code blocks (```json or ```) or adding any extra text, explanations, or comments:

        {{
            "questions": [
                {{
                    "question": "Question text here",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": "Option X"
                }},
                ...
            ]
        }}

        If the content is insufficient to generate questions, return an empty quiz:

        {{
            "questions": []
        }}

        Content:
        {markdown_content}
        """

        # Query Gemini
        response = llm.complete(prompt)
        raw_response = response.text
        logger.info(f"Raw Gemini response: {raw_response}")

        # Clean response: remove Markdown code block markers and extra whitespace
        cleaned_response = re.sub(r'^```json\s*|\s*```$', '', raw_response).strip()
        logger.info(f"Cleaned response for JSON parsing: {cleaned_response}")

        # Parse JSON response
        try:
            quiz_data = json.loads(cleaned_response)
            logger.info(f"Parsed quiz data: {quiz_data}")

            # Save quiz to JSON file
            quiz_path = Path(settings.OUTPUT_DIR) / f"quiz_{file_id}.json"
            with open(quiz_path, "w", encoding="utf-8") as f:
                json.dump(quiz_data, f, indent=2)
            logger.info(f"Quiz saved to {quiz_path}")

            return quiz_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response after cleaning: {cleaned_response}")
            return {"questions": [], "error": f"Failed to parse LLM response: {str(e)}"}

    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return {"questions": [], "error": f"Error generating quiz: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    file_id = "9bcf4988-bf9e-472d-8fae-94ec5ba6d456"  # Replace with your file_id
    num_questions = 5
    result = test_gemini(file_id, num_questions)
    print(json.dumps(result, indent=2))