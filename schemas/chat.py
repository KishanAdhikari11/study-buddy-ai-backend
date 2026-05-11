from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    source: UUID
    text: str


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10


class ChatResponse(BaseModel):
    answer: str
    context: Optional[str]
    retrieved_chunks: Optional[list[RetrievedChunk]] = []
