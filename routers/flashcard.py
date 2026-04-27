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
from models import Embedding, FlashCard
from schemas.common import ErrorResponseSchema
from schemas.flashcards import FlashcardRequests, FlashcardResponse, FlashcardSchema
from services.auth_service import get_db_file, get_db_user
from utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/flashcards",
    responses={403: {"model": ErrorResponseSchema}},
)

FLASHCARD_PROMPT = """You are a flashcard generator. Based on the following text content, generate flashcards for studying.

CONTENT:
{content}

Generate exactly {count} flashcards covering the most important concepts.

Respond ONLY with a valid JSON array, no markdown, no explanation:
[
  {{
    "front": "What is ...?",
    "back": "It is ...",
    "explanation": "Explanation of the answer"
  }}
]"""


def build_cards(flashcards: Sequence[FlashCard]) -> list[FlashcardSchema]:
    return [
        FlashcardSchema(
            id=str(fc.id),
            front=fc.question,
            back=fc.answer,
            explanation=fc.explanation,
            remember=fc.remember,
        )
        for fc in flashcards
    ]


def parse_raw(raw) -> str:
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
    return raw


@router.post("/generate/{file_id}", response_model=FlashcardResponse)
async def generate_flashcards(
    file_id: UUID,
    payload: FlashcardRequests,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlashcardResponse:
    db_user = await get_db_user(auth_user, db)
    await get_db_file(file_id, db_user.id, db)

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
    prompt = FLASHCARD_PROMPT.format(content=content, count=payload.count)
    response = await llm.ainvoke(prompt)

    raw = parse_raw(response.content)

    try:
        cards = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse flashcards from AI",
        )

    try:
        db_cards = []
        for card in cards:
            fc = FlashCard(
                user_id=db_user.id,
                file_id=file_id,
                question=card.get("front", ""),
                answer=card.get("back", ""),
                explanation=card.get("explanation", ""),
                remember=None,
            )
            db.add(fc)
            db_cards.append(fc)

        await db.commit()
        for fc in db_cards:
            await db.refresh(fc)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save flashcards: {str(e)}",
        )

    return FlashcardResponse(file_id=file_id, cards=build_cards(db_cards))


@router.get("/list", response_model=list[FlashcardResponse])
async def list_flashcards(
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FlashcardResponse]:
    db_user = await get_db_user(auth_user, db)

    result = await db.execute(
        select(FlashCard.file_id).where(FlashCard.user_id == db_user.id).distinct()
    )
    file_ids = result.scalars().all()

    db_file = await get_db_file(file_ids[0], db_user.id, db)

    responses = []
    for file_id in file_ids:
        fc_result = await db.execute(
            select(FlashCard).where(FlashCard.file_id == file_id)
        )
        flashcards = fc_result.scalars().all()
        responses.append(
            FlashcardResponse(
                file_id=file_id,
                file_name=db_file.filename,
                cards=build_cards(flashcards),
            )
        )

    return responses


@router.get("/{file_id}", response_model=FlashcardResponse)
async def get_flashcards(
    file_id: UUID,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlashcardResponse:
    db_user = await get_db_user(auth_user, db)
    db_file = await get_db_file(file_id, db_user.id, db)

    result = await db.execute(select(FlashCard).where(FlashCard.file_id == file_id))
    flashcards = result.scalars().all()

    return FlashcardResponse(
        file_id=file_id, file_name=db_file.filename, cards=build_cards(flashcards)
    )


@router.patch("/{flashcard_id}/remember", response_model=FlashcardSchema)
async def toggle_remember(
    flashcard_id: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlashcardSchema:
    db_user = await get_db_user(auth_user, db)

    result = await db.execute(
        select(FlashCard).where(
            FlashCard.id == flashcard_id,
            FlashCard.user_id == db_user.id,
        )
    )
    fc = result.scalar_one_or_none()
    if not fc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found",
        )

    fc.remember = not fc.remember if fc.remember is not None else True
    await db.commit()
    await db.refresh(fc)

    return build_cards([fc])[0]
