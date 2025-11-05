from fastapi import APIRouter, Depends, HTTPException, status

from core.security import get_current_user
from schemas.quiz import QuizRequest, QuizResponse
from utils.logger import get_logger
from utils.quizzes import generate_quiz_from_index

logger = get_logger()
router = APIRouter(dependencies=[Depends(get_current_user)])


def _normalize_count(count: int | None) -> int:
    """Convert None/-1 → 0 for auto-distribution, else return count."""
    return 0 if count is None or count == -1 else count


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_200_OK)
async def generate_quiz_endpoint(request: QuizRequest):
    try:
        single = _normalize_count(request.num_single_correct)
        multi = _normalize_count(request.num_multiple_correct)
        yesno = _normalize_count(request.num_yes_no)

        # Validate total
        specified_total = single + multi + yesno
        if specified_total > request.total_questions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Sum of specified question types exceeds total_questions.",
            )

        quiz_result = generate_quiz_from_index(
            file_id=request.file_id,
            total_questions=request.total_questions,
            num_single_correct=single,
            num_multiple_correct=multi,
            num_yes_no=yesno,
            language=request.language,
            quizzes_type=request.quizzes_type,
        )

        # Convert dict → QuizResponse (pydantic will validate)
        return QuizResponse(**quiz_result)

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception(
            "Unexpected error for file_id", extra={"file_id": request.file_id}
        )
        raise HTTPException(status_code=500, detail="Unexpected error")
