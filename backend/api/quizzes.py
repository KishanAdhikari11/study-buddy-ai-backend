from fastapi import APIRouter, HTTPException
from utils.quizzies import generate_quiz_from_index
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class QuizRequest(BaseModel):
    file_id: str
    num_questions: int = 5

@router.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    try:
        quiz_data = generate_quiz_from_index(request.file_id, request.num_questions)
        if not quiz_data.get("questions"):
            logger.error(f"Failed to generate quiz for file_id: {request.file_id}")
            raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {quiz_data.get('error', 'No questions generated')}")
        logger.info(f"Quiz generated for file_id: {request.file_id}")
        return quiz_data
    except Exception as e:
        logger.error(f"Error generating quiz for file_id: {request.file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")