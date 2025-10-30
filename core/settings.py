import os
from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")
    UPLOAD_DIR: str = ""
    OUTPUT_DIR: str = ""
    
    # Database settings
    DB_URL: str = "postgresql+asyncpg://postgres:password@localhost:5433/s"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Pinecone settings
    PINECONE_ENV: str = ""
    PINECONE_INDEX_NAME: str = ""
    
    # Gemini API Key
    GEMINI_API_KEY: str = ""
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"


settings = Settings()
