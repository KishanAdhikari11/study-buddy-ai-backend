import json
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from langchain.chat_models import init_chat_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.settings import settings
from db import get_db
from models import Embedding, Quiz
from schemas.common import ErrorResponseSchema
from schemas.quizzes import MCQQuestion, QuizRequest, QuizzesResponse, TrueFalseQuestion
from services.auth_service import get_db_file, get_db_user
from utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/quiz",
    responses={403: {"model": ErrorResponseSchema}},
)

QUIZ_PROMPT = """You are a quiz generator. Based on the following text content, generate a quiz.

CONTENT:
{content}

Generate exactly {count} questions. Mix of MCQ and True/False.

Respond ONLY with a valid JSON array, no markdown, no explanation:
[
  {{
    "type": "mcq",
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "explanation": "Explanation of the answer"
  }},
  {{
    "type": "truefalse",
    "question": "...",
    "answer": "True",
    "explanation": "Explanation of the answer"
  }}
]"""


def build_questions(quizzes: Sequence[Quiz]) -> list[MCQQuestion | TrueFalseQuestion]:
    questions = []
    for quiz in quizzes:
        options = [quiz.option_1, quiz.option_2, quiz.option_3, quiz.option_4]
        options = [opt for opt in options if opt and opt.strip()]

        is_tf = len(options) == 2 and set(options) == {"True", "False"}

        answer = ""
        if quiz.correct_option and 1 <= quiz.correct_option <= len(options):
            answer = options[quiz.correct_option - 1]

        questions.append(
            {
                "type": "truefalse" if is_tf else "mcq",
                "question": quiz.question,
                "options": options,
                "answer": answer,
                "explanation": quiz.explanation,
            }
        )
    return questions


@router.post("/generate/{file_id}", response_model=QuizzesResponse)
async def generate_quiz(
    file_id: UUID,
    payload: QuizRequest,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizzesResponse:
    db_user = await get_db_user(auth_user, db)
    db_file = await get_db_file(file_id, db_user.id, db)

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    result = await db.execute(
        select(Embedding).where(Embedding.file_id == file_id).limit(20)
    )
    embeddings = result.scalars().all()

    if not embeddings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No content found for this file",
        )

    content = "\n\n".join([e.chunks for e in embeddings])[: settings.MAX_TOKENS]

    llm = init_chat_model(settings.AI_MODEL, model_provider="google_genai")
    prompt = QUIZ_PROMPT.format(content=content, count=payload.count)

    response = await llm.ainvoke(prompt)
    raw = response.content
    if isinstance(raw, list):
        raw = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in raw
        ).strip()
    else:
        raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse quiz from AI",
        )
    try:
        for q in questions:
            options = q.get("options", [])

            if q.get("type") == "truefalse":
                options = ["True", "False"]

            answer = q.get("answer", "")
            correct_option = None

            if answer in options:
                correct_option = options.index(answer) + 1

            quiz = Quiz(
                user_id=db_user.id,
                file_id=file_id,
                question=q.get("question", ""),
                correct_option=correct_option,
                explanation=q.get("explanation", ""),
                option_1=options[0] if len(options) > 0 else "",
                option_2=options[1] if len(options) > 1 else "",
                option_3=options[2] if len(options) > 2 else "",
                option_4=options[3] if len(options) > 3 else "",
            )

            db.add(quiz)

        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save quiz: {str(e)}",
        )

    return QuizzesResponse(file_id=file_id, questions=questions)


@router.get("/list", response_model=list[QuizzesResponse])
async def list_quizzes(
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[QuizzesResponse]:
    db_user = await get_db_user(auth_user, db)

    result = await db.execute(
        select(Quiz.file_id).where(Quiz.user_id == db_user.id).distinct()
    )
    file_ids = result.scalars().all()
    file = await get_db_file(file_ids[0], db_user.id, db)
    file_name = file.filename if file else "Unknown"

    responses = []
    for file_id in file_ids:
        quizzes_result = await db.execute(select(Quiz).where(Quiz.file_id == file_id))
        quizzes = quizzes_result.scalars().all()
        responses.append(
            QuizzesResponse(
                file_name=file_name,
                file_id=file_ids[0],
                questions=build_questions(quizzes),
            )
        )

    return responses


@router.get("/{file_id}", response_model=QuizzesResponse)
async def get_quiz(
    file_id: UUID,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizzesResponse:
    db_user = await get_db_user(auth_user, db)
    db_file = await get_db_file(file_id, db_user.id, db)

    result = await db.execute(select(Quiz).where(Quiz.file_id == file_id))
    quizzes = result.scalars().all()

    return QuizzesResponse(
        file_id=file_id,
        file_name=db_file.filename if db_file else "Unknown",
        questions=build_questions(quizzes),
    )
