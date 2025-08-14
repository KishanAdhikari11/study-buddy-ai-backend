from fastapi import APIRouter, HTTPException, status
import logging
from models.Quiz import QuizRequest, QuizResponse
from utils.quizzes import generate_quiz_from_index

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"],
)

@router.post(
    "/generate", 
    response_model=QuizResponse, 
    summary="Generate a quiz from document content",
    description="""
    Generates a new quiz based on the content of a specified document (`file_id`).
    Users can define the `total_questions` and optionally specify the exact counts
    for `single_correct`, `multiple_correct`, and `yes_no` question types.
    The quiz questions will be generated in the `language` specified.
    """,
    status_code=status.HTTP_200_OK, # HTTP status code for a successful response
    responses={
        status.HTTP_404_NOT_FOUND: { # Response for when the source file is not found
            "description": "The specified document file was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Markdown file not found: example_file.md"}
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: { # Response for invalid request parameters or insufficient content
            "description": "The request was well-formed but could not be processed due to semantic errors (e.g., invalid question counts, empty content).",
            "content": {
                "application/json": {
                    "example": {"detail": "Sum of specified question types exceeds total_questions."}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: { # General server error response
            "description": "An unexpected error occurred on the server during quiz generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected server error occurred: LLM generation failed."}
                }
            }
        },
    }
)
async def generate_quiz_endpoint(request: QuizRequest):
    """
    Handles the request to generate a quiz.
    It calls the `generate_quiz_from_index` utility function,
    which interfaces with the LLM and processes the document content.
    Error handling and response formatting are managed here.
    """
    try:
        # Call the core quiz generation logic, passing all parameters from the request.
        # The generate_quiz_from_index function returns a dictionary.
        quiz_result = generate_quiz_from_index(
            file_id=request.file_id,
            total_questions=request.total_questions,
            num_single_correct=request.num_single_correct,
            num_multiple_correct=request.num_multiple_correct,
            num_yes_no=request.num_yes_no,
            language=request.language,
            quizzes_type=request.quizzes_type
        )

        # Check if the utility function returned an explicit error message.
        if "error" in quiz_result and quiz_result["error"]:
            error_message = quiz_result["error"]
            logger.error(f"Quiz generation utility returned an error for file_id '{request.file_id}': {error_message}")

            # Map specific error messages from the utility function to appropriate HTTP status codes.
            if "Markdown file not found" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message
                )
            elif "No content in Markdown file" in error_message or \
                 "Sum of specified question types exceeds total_questions" in error_message or \
                 "No question types selected for generation" in error_message or \
                 "Invalid quiz structure" in error_message or \
                 "Invalid question format" in error_message or \
                 "Invalid question: " in error_message: # Catch various validation errors from utility
                 raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_message
                )
            else:
                # Default to 500 for other internal errors from the utility function.
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error generating quiz: {error_message}"
                )

        # If no questions were generated but no explicit error was indicated by the utility,
        # it might still be considered a failure to produce valid content.
        if not quiz_result.get("questions"):
            logger.warning(f"Quiz generation completed for file_id '{request.file_id}', but no questions were produced.")
            # Depending on strictness, you might return 200 with empty list and warning, or 500.
            # Here, we raise 500 if no questions are produced, implying a generation failure.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Quiz generation completed but produced no questions. The content might be insufficient, or there was an issue with the LLM's output."
            )

        logger.info(f"Quiz successfully generated for file_id: {request.file_id} with {len(quiz_result.get('questions', []))} questions.")
        
        return quiz_result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"An unhandled exception occurred during quiz generation for file_id: {request.file_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred during quiz generation: {str(e)}"
        )