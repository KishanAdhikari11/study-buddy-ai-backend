from fastapi import APIRouter, HTTPException

from schemas.flashcards import FlashcardRequest
from utils.flashcards import generate_flashcards
from utils.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/generate-flashcards")
async def generate_flashcards_endpoint(request: FlashcardRequest):
    try:
        flashcard_data = generate_flashcards(
            file_id=request.file_id,
            num_cards=request.total_flashcards,
            language=request.language,
        )
        flashcards = flashcard_data.get("flashcards", [])

        if not flashcards:
            logger.error(
                "Failed to generate flashcards",
                extra={"file_id": request.file_id, "language": request.language},
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate flashcards: {flashcard_data.get('error', 'No flashcards generated')}",
            )

        logger.info(
            "Flashcards generated",
            extra={"file_id": request.file_id, "language": request.language},
        )
        return {"flashcards": flashcards}
    except Exception as e:
        logger.error(
            "Error generating flashcards",
            extra={
                "file_id": request.file_id,
                "language": request.language,
                "error": e,
            },
        )
        raise HTTPException(status_code=500, detail="Error generating flashcards")
