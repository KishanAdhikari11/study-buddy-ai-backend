import json
import logging
import re
from pathlib import Path

from core.dependencies import get_llm
from core.settings import settings

logger = logging.getLogger(__name__)


def generate_quiz_from_index(
    file_id: str,
    total_questions: int,
    num_single_correct: int = -1,
    num_multiple_correct: int = -1,
    num_yes_no: int = -1,
    language: str = "en",
    quizzes_type: str = "mixed",
) -> dict:
    try:
        llm = get_llm()
        logger.info("Gemini LLM initialized")

        markdown_path = Path(settings.OUTPUT_DIR) / f"{file_id}.md"
        if not markdown_path.exists():
            logger.error(
                "Markdown file not found", extra={"markdown_path": markdown_path}
            )
            return {
                "questions": [],
                "error": f"Markdown file not found: {markdown_path}",
            }

        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        logger.info("Markdown content loaded", extra={"markdown_path": markdown_path})

        if not markdown_content.strip():
            logger.warning("Markdown content is empty")
            return {"questions": [], "error": "No content in Markdown file"}

        question_counts = {
            "single_correct": num_single_correct,
            "multiple_correct": num_multiple_correct,
            "yes_no": num_yes_no,
        }

        explicit_counts = {k: v for k, v in question_counts.items() if v >= 0}
        sum_explicit_counts = sum(explicit_counts.values())

        if sum_explicit_counts > total_questions:
            return {
                "questions": [],
                "error": "Sum of specified question types exceeds total_questions.",
            }

        remaining_questions = total_questions - sum_explicit_counts
        auto_distribute_types = [k for k, v in question_counts.items() if v == -1]

        if not explicit_counts:
            auto_distribute_types = ["single_correct", "multiple_correct", "yes_no"]

        if remaining_questions > 0 and auto_distribute_types:
            num_auto_distribute_types = len(auto_distribute_types)
            base_count = remaining_questions // num_auto_distribute_types
            remainder = remaining_questions % num_auto_distribute_types

            for i, q_type in enumerate(auto_distribute_types):
                question_counts[q_type] = base_count + (1 if i < remainder else 0)
        elif (
            remaining_questions == 0
            and not auto_distribute_types
            and sum_explicit_counts < total_questions
        ):
            if len(explicit_counts) > 0:
                first_explicit_type = list(explicit_counts.keys())[0]
                question_counts[first_explicit_type] += (
                    total_questions - sum_explicit_counts
                )
            else:
                return {
                    "questions": [],
                    "error": "Cannot fulfill total_questions with given constraints.",
                }

        for k in question_counts:
            if question_counts[k] == -1:
                question_counts[k] = 0

        question_distribution_instruction = []
        if question_counts["single_correct"] > 0:
            question_distribution_instruction.append(
                f"- Exactly {question_counts['single_correct']} Single-Correct Multiple-Choice questions."
            )
        if question_counts["multiple_correct"] > 0:
            question_distribution_instruction.append(
                f"- Exactly {question_counts['multiple_correct']} Multiple-Correct Multiple-Choice questions."
            )
        if question_counts["yes_no"] > 0:
            question_distribution_instruction.append(
                f"- Exactly {question_counts['yes_no']} Yes/No questions."
            )

        if not question_distribution_instruction:
            return {
                "questions": [],
                "error": "No question types selected for generation.",
            }

        question_distribution_str = "\n        ".join(question_distribution_instruction)
        prompt = f"""
        You are an expert educational content creator and quiz generator. Your task is to construct a quiz based on the provided content from a PDF document.

        The quiz must contain exactly {total_questions} questions.
        All questions, options, and answers MUST be in the {language} language.

        Strictly adhere to the following distribution of question types:
        {question_distribution_str}

        Here are the specific requirements for each question type:
        1.  **Single-Correct Multiple-Choice (SCMC):** Exactly 1 correct answer out of 4 distinct options.
        2.  **Multiple-Correct Multiple-Choice (MCMC):** 2 or more correct answers out of 4 distinct options. The question text MUST include a localized phrase equivalent to "(select all that apply)" in the target {language} language.
        3.  **Yes/No (YN):** Exactly 2 options: ["Yes", "No"] (or their {language} equivalents, e.g., ["Sí", "No"], ["Oui", "Non"]), with 1 correct answer.

        Your response MUST be a raw JSON object, ensuring strict adherence to valid JSON syntax. Do NOT wrap the JSON in markdown code blocks (```json or ```), or add any extra text, explanations, or comments before or after the JSON.

        Here are examples of the exact JSON format and question types you should generate. Note that the content of questions, options, and answers should be localized to the specified {language}, while the JSON keys (e.g., "type", "question", "options", "correct_answers") remain in English:

        ### Example 1 (Single-Correct Multiple-Choice - English)
        {{
            "type": "single_correct",
            "question": "What is the primary function of the mitochondria in a eukaryotic cell?",
            "options": ["Protein synthesis", "Energy production", "Waste removal", "Cellular respiration of nutrients"],
            "correct_answers": ["Energy production"]
        }}

        ### Example 2 (Multiple-Correct Multiple-Choice - Spanish Example)
        {{
            "type": "multiple_correct",
            "question": "¿Cuáles de los siguientes son planetas rocosos en nuestro sistema solar? (selecciona todos los que apliquen)",
            "options": ["Mercurio", "Júpiter", "Tierra", "Neptuno"],
            "correct_answers": ["Mercurio", "Tierra"]
        }}

        ### Example 3 (Yes/No - French Example)
        {{
            "type": "yes_no",
            "question": "Le soleil est-il une étoile?",
            "options": ["Oui", "Non"],
            "correct_answers": ["Oui"]
        }}
        
        ---

        **Instructions for Quiz Generation:**
        - **Overall:** Generate exactly {total_questions} questions. Prioritize creating high-quality, relevant questions directly from the "Content" provided below.
        - **Language:** Ensure all generated questions, options, and correct answers are strictly in the {language} language.
        - **Single-Correct:** Must have exactly 4 options and exactly 1 correct answer.
        - **Multiple-Correct:** Must have exactly 4 options and 2 or more correct answers. The question text MUST explicitly include a localized phrase equivalent to "(select all that apply)" (case-insensitive) for the {language} language.
        - **Yes/No:** Must have exactly 2 options: ["Yes", "No"] (or their exact {language} equivalents like ["Sí", "No"], ["Oui", "Non"]). Must have exactly 1 correct answer, which is one of the two provided options.
        - All values in "correct_answers" must be present verbatim in the "options" list.
        - Questions should test understanding of the provided "Content", not general knowledge.

        If the provided "Content" is insufficient to generate the requested number and quality of questions, or if it's entirely unrelated to quiz generation, return an empty quiz object as follows:

        {{
            "questions": []
        }}

        Content to use for quiz generation:
        {markdown_content}
        """

        response = llm.complete(prompt)
        raw_response = response.text
        cleaned_response = re.sub(r"^```json\s*|\s*```$", "", raw_response).strip()

        try:
            quiz_data = json.loads(cleaned_response)
            logger.info("Parsed quiz data", extra={"quiz_data": quiz_data})

            if not isinstance(quiz_data, dict) or "questions" not in quiz_data:
                logger.error("Invalid quiz structure: missing 'questions' key")
                return {"questions": [], "error": "Invalid quiz structure"}

            generated_counts = {"single_correct": 0, "multiple_correct": 0, "yes_no": 0}
            for question in quiz_data.get("questions", []):
                q_type = question.get("type")
                if q_type in generated_counts:
                    generated_counts[q_type] += 1

            for q_type, expected_count in question_counts.items():
                if expected_count > 0 and generated_counts[q_type] != expected_count:
                    logger.warning(
                        "Mismatch in question counts",
                        extra={
                            "question_type": q_type,
                            "expected": expected_count,
                            "generated": generated_counts[q_type],
                        },
                    )

            if len(quiz_data.get("questions", [])) != total_questions:
                logger.error("Total questions generated does not match requested total")
                return {
                    "questions": [],
                    "error": "Total questions generated does not match requested total",
                }

            for question in quiz_data.get("questions", []):
                if not isinstance(question, dict):
                    logger.error("Invalid question format")
                    return {"questions": [], "error": "Invalid question format"}

                q_type_raw = question.get("type")
                if not isinstance(q_type_raw, str):
                    logger.warning(
                        "Invalid or missing question type", extra={"question": question}
                    )
                    continue

                q_type = q_type_raw.strip().lower()
                if q_type not in ["single_correct", "multiple_correct", "yes_no"]:
                    logger.error(
                        "Invalid question type", extra={"question_type": q_type}
                    )
                    return {
                        "questions": [],
                        "error": f"Invalid question type: {q_type}",
                    }

                options = question.get("options", [])
                correct_answers = question.get("correct_answers", [])

                if not all(isinstance(opt, str) and opt.strip() for opt in options):
                    logger.error("Invalid question: options must be non-empty strings")
                    return {
                        "questions": [],
                        "error": "Invalid question: options must be non-empty strings",
                    }

                if len(options) != len(set(options)):
                    logger.error("Invalid question: options must be unique")
                    return {
                        "questions": [],
                        "error": "Invalid question: options must be unique",
                    }

                if not all(ca in options for ca in correct_answers):
                    logger.error(
                        "Invalid question: correct_answers must be from options"
                    )
                    return {
                        "questions": [],
                        "error": "Invalid question: correct_answers must be from options",
                    }

                # Type-specific validation
                if q_type == "single_correct":
                    if len(options) != 4 or len(correct_answers) != 1:
                        logger.error(
                            "Invalid single_correct question: must have 4 options and 1 correct answer, got 4 options and 1 correct answer"
                        )
                        return {
                            "questions": [],
                            "error": "Invalid single_correct question format",
                        }
                elif q_type == "multiple_correct":
                    if len(options) != 4 or len(correct_answers) < 2:
                        logger.error(
                            "Invalid multiple_correct question: must have 4 options and 2 or more correct answers, got 4 options and 1 correct answer"
                        )
                        return {
                            "questions": [],
                            "error": "Invalid multiple_correct question format",
                        }
                elif q_type == "yes_no":
                    if len(options) != 2 or len(correct_answers) != 1:
                        logger.error(
                            "Invalid yes_no question: must have 2 options and 1 correct answer, got options {options} and {len(correct_answers)} correct answers"
                        )
                        return {
                            "questions": [],
                            "error": "Invalid yes_no question format",
                        }

            quiz_path = Path(settings.OUTPUT_DIR) / f"quiz_{file_id}.json"
            with open(quiz_path, "w", encoding="utf-8") as f:
                json.dump(quiz_data, f, indent=2)
            logger.info("Quiz saved", extra={"quiz_path": quiz_path})

            return quiz_data
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response after cleaning: {cleaned_response}")
            return {"questions": [], "error": f"Failed to parse LLM response: {str(e)}"}

    except Exception as e:
        logger.error("Error generating quiz", exc_info=e)
        return {"questions": [], "error": "Error generating quiz"}
