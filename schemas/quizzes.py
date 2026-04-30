from typing import Annotated, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class MCQQuestion(BaseModel):
    type: Literal["mcq"] = "mcq"
    question: str
    options: list[str]
    answer: str
    explanation: str


class TrueFalseQuestion(BaseModel):
    type: Literal["truefalse"] = "truefalse"
    question: str
    options: list[str] = ["True", "False"]
    answer: str
    explanation: str


Question = Annotated[Union[MCQQuestion, TrueFalseQuestion], Field(discriminator="type")]


class QuizRequest(BaseModel):
    count: int = Field(default=10, gt=0, le=50)


class QuizzesResponse(BaseModel):
    file_name: Optional[str] = None
    file_id: UUID
    questions: list[Question]
