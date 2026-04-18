from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DB_URL: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # supabase setting
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET: str = ""
    MAX_FILE_SIZE_MB: int = 30 * 1024 * 1024  # 30 MB

    # Gemini API Key
    GEMINI_API_KEY: str = ""

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"


settings = Settings()
