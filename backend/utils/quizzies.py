from core.dependencies import get_llm
from core.config import settings
from pathlib import Path
import json
import logging
import re

logger = logging.getLogger(__name__)

def generate_quiz_from_index(file_id: str, num_questions: int, language: str = "en", quizzes_type: str = "mixed") -> dict:
    try:
        llm = get_llm()
        logger.info("Gemini LLM initialized")

        # Read Markdown file using file_id
        markdown_path = Path(settings.OUTPUT_DIR) / f"{file_id}.md"
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
        You are a quiz generator. Using the following content extracted from a PDF, create a quiz with exactly {num_questions} questions in {language} language. The quiz should include a mix of three question types: 
        - Single-correct multiple-choice (exactly 1 correct answer, 4 answer options)
        - Multiple-correct multiple-choice (2 or more correct answers, 4 answer options)
        - Yes/No (exactly 2 answer options: "Yes" and "No", 1 correct answer)

        Distribute the questions roughly evenly among the three types, prioritizing variety. Return the quiz as a raw JSON object, ensuring valid JSON syntax, without wrapping it in code blocks (```json or ```) or adding any extra text, explanations, or comments:

        {{
            "questions": [
                {{
                    "type": "single_correct",
                    "question": "Question text here",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answers": ["Option X"]
                }},
                {{
                    "type": "multiple_correct",
                    "question": "Question text here (select all that apply)",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answers": ["Option X", "Option Y", ...]
                }},
                {{
                    "type": "yes_no",
                    "question": "Question text here",
                    "options": ["Yes", "No"],
                    "correct_answers": ["Yes"] // or ["No"]
                }},
                ...
            ]
        }}

        Ensure:
        - Single-correct questions have exactly 4 options and 1 correct answer.
        - Multiple-correct questions have exactly 4 options, 2 or more correct answers, and include "select all that apply" in the question text.
        - Yes/No questions have exactly 2 options ("Yes" and "No") and 1 correct answer.
        - All correct_answers values are from the options list.
        - Questions are relevant to the provided content.

        If the content is insufficient to generate the requested number of questions, return an empty quiz:

        {{
            "questions": []
        }}

        Content:
        {markdown_content}
        """

        response = llm.complete(prompt)
        raw_response = response.text
        logger.info(f"Raw LLM response: {raw_response}")
        cleaned_response = re.sub(r'^```json\s*|\s*```$', '', raw_response).strip()
        logger.info(f"Cleaned response for JSON parsing: {cleaned_response}")

        try:
            quiz_data = json.loads(cleaned_response)
            logger.info(f"Parsed quiz data: {quiz_data}")

            # Validate quiz structure
            if not isinstance(quiz_data, dict) or "questions" not in quiz_data:
                logger.error("Invalid quiz structure: missing 'questions' key")
                return {"questions": [], "error": "Invalid quiz structure"}

            for question in quiz_data.get("questions", []):
                if not isinstance(question, dict):
                    logger.error("Invalid question format")
                    return {"questions": [], "error": "Invalid question format"}
                
                q_type = question.get("type")
                if q_type not in ["single_correct", "multiple_correct", "yes_no"]:
                    logger.error(f"Invalid question type: {q_type}")
                    return {"questions": [], "error": f"Invalid question type: {q_type}"}
                
                options = question.get("options", [])
                correct_answers = question.get("correct_answers", [])
                
                # Validate common properties
                if not all(isinstance(opt, str) and opt.strip() for opt in options):
                    logger.error("Invalid question: options must be non-empty strings")
                    return {"questions": [], "error": "Invalid question: options must be non-empty strings"}
                
                if not all(ca in options for ca in correct_answers):
                    logger.error("Invalid question: correct_answers must be from options")
                    return {"questions": [], "error": "Invalid question: correct_answers must be from options"}

                # Type-specific validation
                if q_type == "single_correct":
                    if len(options) != 4 or len(correct_answers) != 1:
                        logger.error(f"Invalid single_correct question: must have 4 options and 1 correct answer, got {len(options)} options and {len(correct_answers)} correct answers")
                        return {"questions": [], "error": "Invalid single_correct question format"}
                elif q_type == "multiple_correct":
                    if len(options) != 4 or len(correct_answers) < 2:
                        logger.error(f"Invalid multiple_correct question: must have 4 options and 2 or more correct answers, got {len(options)} options and {len(correct_answers)} correct answers")
                        return {"questions": [], "error": "Invalid multiple_correct question format"}
                    if "select all that apply" not in question.get("question", "").lower():
                        logger.error("Invalid multiple_correct question: question text must include 'select all that apply'")
                        return {"questions": [], "error": "Invalid multiple_correct question: missing 'select all that apply' in question text"}
                elif q_type == "yes_no":
                    if options != ["Yes", "No"] or len(correct_answers) != 1:
                        logger.error(f"Invalid yes_no question: must have options ['Yes', 'No'] and 1 correct answer, got options {options} and {len(correct_answers)} correct answers")
                        return {"questions": [], "error": "Invalid yes_no question format"}

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