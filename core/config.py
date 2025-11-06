from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    PINECONE_API_KEY: str
    UPLOAD_DIR: str = str(Path("static/uploads"))
    OUTPUT_DIR: str = str(Path("static/outputs"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
