from contextlib import asynccontextmanager
from typing import Awaitable, Callable
from uuid import uuid4

import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.settings import settings
from db import sessionmanager
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.file_upload import router as file_upload_router
from routers.flashcard import router as flashcard_router
from routers.quizzes import router as quiz_router
from routers.yt_transcribe import router as yt_transcribe_router
from schemas.common import ErrorResponseSchema
from utils.limiter import limiter
from utils.logger import RequestContextVar, get_logger, request_ctx_var

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not sessionmanager.session_factory:
        sessionmanager.init_db()

    try:
        app.state.redis = await redis.from_url(settings.REDIS_URL)

        yield

    except Exception:
        logger.exception("Failed to load embedding model")

    finally:
        if hasattr(app.state, "embedding_model"):
            del app.state.embedding_model
        if hasattr(app.state, "redis"):
            await app.state.redis.close()
        await sessionmanager.close()


app = FastAPI(
    title="AI Study Buddy",
    lifespan=lifespan,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ErrorResponseSchema,
            "description": "Rate Limit Response",
        }
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceed_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"detail": "Rate limit exceeded"},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    return response


@app.middleware("http")
async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid4())
    request_path = f"{request.method} {request.url.path}"
    request_ctx_var.set(
        RequestContextVar(request_id=request_id, request_path=request_path)
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(file_upload_router, prefix="/api", tags=["File Upload"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(flashcard_router, prefix="/api", tags=["Flashcards"])
app.include_router(quiz_router, prefix="/api", tags=["Quizzes"])
app.include_router(yt_transcribe_router, prefix="/api", tags=["YouTube Transcription"])


@app.get("/", tags=["Health"])
async def healthz(request: Request) -> str:
    return "ok"
