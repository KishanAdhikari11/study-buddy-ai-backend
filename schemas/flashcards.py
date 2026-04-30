from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FlashcardRequests(BaseModel):
    count: int = Field(default=15, ge=1, le=50)


class FlashcardSchema(BaseModel):
    id: str
    front: str
    back: str
    explanation: str
    remember: bool | None = None


class FlashcardResponse(BaseModel):
    file_id: UUID
    file_name: Optional[str] = None
    cards: list[FlashcardSchema]


class FlashcardListResponse(BaseModel):
    file_id: UUID
    file_name: Optional[str] = None
