from contextlib import asynccontextmanager
from pathlib import Path
from typing import Awaitable, Callable
from uuid import uuid4

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.settings import settings
from db import sessionmanager
from routers.auth import router as auth_router
from routers.file_upload import router as file_upload_router
from schemas.common import ErrorResponseSchema
from schemas.exception import EmbedingModelError
from utils.limiter import limiter
from utils.logger import RequestContextVar, get_logger, request_ctx_var

logger = get_logger()


_MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL_PATH = Path("models") / _MODEL_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not sessionmanager.session_factory:
        sessionmanager.init_db()

    model = None
    try:
        if _MODEL_PATH.exists():
            logger.info(
                "Loading embedding model from disk",
                extra={"model_name": _MODEL_NAME, "model_path": _MODEL_PATH},
            )
            model = SentenceTransformer(str(_MODEL_PATH))
        else:
            logger.info(
                "Downloading embedding model from HuggingFace",
                extra={"model_name": _MODEL_NAME},
            )
            model = SentenceTransformer(_MODEL_NAME)
            model.save(str(_MODEL_PATH))
            logger.info(
                "Embedding model saved to disk",
                extra={"model_name": _MODEL_NAME, "model_path": _MODEL_PATH},
            )

        app.state.embedding_model = model
        app.state.redis = await aioredis.from_url(settings.REDIS_URL)

        yield

    except Exception as e:
        logger.exception("Failed to load embedding model")
        raise EmbedingModelError(f"Error loading embedding model: {e}")

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

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceed_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"detail": "Rate limit exceeded"},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    response = request.app.state.limiter._inject_headers(
        response, getattr(request.state, "view_rate_limit", None)
    )
    return response


app.add_middleware(SlowAPIMiddleware)


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


app.include_router(file_upload_router, prefix="/api/file", tags=["File Upload"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])


@app.get("/", tags=["Health"])
async def healthz(request: Request) -> str:
    return "ok"
