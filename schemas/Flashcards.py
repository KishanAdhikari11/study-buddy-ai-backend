from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FlashcardBase(BaseModel):
    """Base Flashcard model with common attributes"""

    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The answer text")
    context: Optional[str] = Field(
        None, description="Additional context or explanation"
    )


class FlashcardCreate(FlashcardBase):
    """Schema for creating a new flashcard"""

    topic: str = Field(..., description="Topic or subject of the flashcard")
    source_material_id: str = Field(..., description="ID of the uploaded PDF/notes")


class FlashcardInDB(FlashcardBase):
    """Schema for flashcard as stored in database"""

    id: str = Field(..., description="Unique identifier")
    user_id: str = Field(..., description="ID of user who created the flashcard")
    topic: str
    source_material_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class FlashcardResponse(FlashcardInDB):
    """Schema for returning flashcard data"""

    pass


class FlashcardBatch(BaseModel):
    """Schema for a batch of flashcards"""

    topic: str
    source_material_id: str = Field(..., description="ID of the uploaded PDF/notes")
    flashcards: List[FlashcardCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Machine Learning",
                "source_material_id": "pdf123",
                "flashcards": [
                    {
                        "question": "What is supervised learning?",
                        "answer": "A type of machine learning where the model learns from labeled training data",
                        "context": "Understanding supervised learning is fundamental to ML",
                        "topic": "Machine Learning Basics",
                        "source_material_id": "pdf123",
                    }
                ],
            }
        }
