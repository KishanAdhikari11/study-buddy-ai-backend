from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

QuizQuestionType = Literal["single_correct", "multiple_correct", "yes_no"]


class QuizQuestion(BaseModel):
    type: QuizQuestionType = Field(..., description="...")
    question: str = Field(..., min_length=5)
    options: List[str] = Field(..., min_length=2)
    correct_answers: List[str] = Field(..., min_length=1)

    @field_validator("correct_answers")
    @classmethod
    def must_be_in_options(cls, v, values):
        options = values.get("options", [])
        if not all(ans in options for ans in v):
            raise ValueError("All correct_answers must be in options")
        return v


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(...)
    error: Optional[str] = None


class QuizRequest(BaseModel):
    file_id: str = Field(...)
    total_questions: int = Field(5, gt=0)
    num_single_correct: Optional[int] = Field(None, ge=-1)
    num_multiple_correct: Optional[int] = Field(None, ge=-1)
    num_yes_no: Optional[int] = Field(None, ge=-1)
    language: str = Field("en")
    quizzes_type: str = Field("mixed")

    @field_validator("num_single_correct", "num_multiple_correct", "num_yes_no")
    @classmethod
    def allow_none_or_neg_one(cls, v):
        if v in (None, -1):
            return v
        if isinstance(v, int) and v >= 0:
            return v
        raise ValueError("Must be None, -1, or non-negative integer")

    def get_normalized_counts(self) -> tuple[int | None, int | None, int | None]:
        return (
            0 if self.num_single_correct in (None, -1) else self.num_single_correct,
            0 if self.num_multiple_correct in (None, -1) else self.num_multiple_correct,
            0 if self.num_yes_no in (None, -1) else self.num_yes_no,
        )
