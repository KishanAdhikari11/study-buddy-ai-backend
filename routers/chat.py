from fastapi import APIRouter, Depends, HTTPException
from langchain.chat_models import init_chat_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from db import get_db
from models import User
from schemas.chat import ChatRequest, ChatResponse
from schemas.common import ErrorResponseSchema
from services.chatbot import ChatContext, ChatState, chatbot, model
from utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/chat",
    responses={
        403: {"model": ErrorResponseSchema, "description": "Forbidden Response"}
    },
)


@router.post("/{file_id}", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    file_id: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    result = await db.execute(select(User).where(User.supabase_id == auth_user))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_context = ChatContext(
        db=db,
        llm=init_chat_model(
            "gemini-3.1-flash-lite-preview", model_provider="google_genai"
        ),
        model=model,
    )

    chat_state = ChatState(
        query=request.query,
        top_k=request.top_k or 10,
        answer="",
        context=None,
        file_id=file_id,
        retrieved_chunks=[],
    )

    final_state = await chatbot.ainvoke(
        input=chat_state,
        context=chat_context,
    )

    return ChatResponse(
        answer=final_state["answer"],
        retrieved_chunks=final_state["retrieved_chunks"],
        context=final_state.get("context"),
    )
