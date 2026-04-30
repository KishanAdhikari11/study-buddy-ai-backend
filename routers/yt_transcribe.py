from fastapi import APIRouter, Depends, HTTPException, status
from langchain.chat_models import init_chat_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.settings import settings
from db import get_db
from models import Youtube
from schemas.common import ErrorResponseSchema
from schemas.youtube import (
    YoutubeListResponse,
    YoutubeResponse,
    YoutubeSummarizeResponse,
)
from services.auth_service import get_db_user
from services.youtube_transcribt import transcribe_yt
from utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/transcribe",
    responses={403: {"model": ErrorResponseSchema}},
)

YT_PREFIX = "https://www.youtube.com/watch?v="
YT_SUMMARIZE_PROMPT = """You are a helpful assistant that summarizes YouTube video transcripts.

TRANSCRIPT:
{transcript}

Please provide a summary of the transcript in a few sentences.
"""

YT_CHAT_PROMPT = """You are a helpful assistant that answers questions based on YouTube video transcripts.
TRANSCRIPT:
{transcript}

USER QUESTION:
{user_message}

ASSISTANT RESPONSE:
"""


@router.post("/", response_model=YoutubeResponse)
async def get_transcribe(
    video_url: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> YoutubeResponse:
    db_user = await get_db_user(auth_user, db)

    if not video_url.startswith(YT_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL",
        )

    video_id = video_url[len(YT_PREFIX) :]
    transcript = transcribe_yt(video_id)
    try:
        yt_entry = Youtube(user_id=db_user.id, url=video_url, transcript=transcript)
        db.add(yt_entry)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error("Failed to save YouTube transcript", extra={"error": e})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save YouTube transcript",
        )
    return YoutubeResponse(url=video_url, transcript=transcript)


@router.get("/summarize", response_model=YoutubeSummarizeResponse)
async def summarize_transcript(
    video_url: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> YoutubeSummarizeResponse:
    await get_db_user(auth_user, db)
    stmt = select(Youtube.transcript).where(Youtube.url == video_url)

    transcript = await db.execute(stmt)
    transcript = transcript.scalars().first()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    prompt = YT_SUMMARIZE_PROMPT.format(transcript=transcript)
    llm = init_chat_model(settings.AI_MODEL, model_provider="google_genai")

    response = await llm.ainvoke(prompt)
    item = response.content[0]

    if isinstance(item, dict):
        content = str(item.get("text", "No summary available"))
    else:
        content = item

    return YoutubeSummarizeResponse(url=video_url, summary=content)


@router.get("/chat", response_model=YoutubeSummarizeResponse)
async def chat_with_yt(
    video_url: str,
    query: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await get_db_user(auth_user, db)
    stmt = select(Youtube.transcript).where(Youtube.url == video_url)

    transcript = await db.execute(stmt)
    transcript = transcript.scalars().first()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    prompt = YT_CHAT_PROMPT.format(transcript=transcript, user_message=query)
    llm = init_chat_model(settings.AI_MODEL, model_provider="google_genai")

    response = await llm.ainvoke(prompt)
    item = response.content[0]

    if isinstance(item, dict):
        content = str(item.get("text", "No summary available"))
    else:
        content = item

    return YoutubeSummarizeResponse(url=video_url, summary=content)


@router.get("/list", response_model=YoutubeListResponse)
async def list_user_videos(
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> YoutubeListResponse:
    db_user = await get_db_user(auth_user, db)
    stmt = select(Youtube.url).where(Youtube.user_id == db_user.id)
    result = await db.execute(stmt)
    urls = result.scalars().all()
    return YoutubeListResponse(url=urls)
