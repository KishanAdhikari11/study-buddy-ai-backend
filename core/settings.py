from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database settings
    DB_URL: str = "postgresql+asyncpg://postgres:password@localhost:5433/s"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Pinecone settings
    PINECONE_ENV: str = ""
    PINECONE_INDEX_NAME: str = ""

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Gemini API Key
    GEMINI_API_KEY: str = ""

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    PINECONE_API_KEY: str = ""
    UPLOAD_DIR: str = str(Path("static/uploads"))
    OUTPUT_DIR: str = str(Path("static/outputs"))


settings = Settings()
