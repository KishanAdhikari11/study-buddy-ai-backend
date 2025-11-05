from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from core.settings import settings
from utils.logger import get_logger

logger = get_logger()


class SessionManager:
    """Manage async DB session"""

    def __init__(self) -> None:
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def init_db(self) -> None:
        self.engine = create_async_engine(
            settings.DB_URL,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
        )

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """yield a db session with correct schema"""
        if not self.session_factory:
            raise RuntimeError("Datasbase session factory isnt initialized")
        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                logger.error("Error in database", extra={"error": e})
                await session.rollback()
                raise RuntimeError(f"Database session error: {e!r}") from e


sessionmanager = SessionManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if not sessionmanager.session_factory:
        sessionmanager.init_db()

    async for session in sessionmanager.get_session():
        yield session

    await sessionmanager.close()
