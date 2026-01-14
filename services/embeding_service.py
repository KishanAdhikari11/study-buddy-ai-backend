from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger

logger = get_logger()


def chunk_text(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],
        chunk_size=400,
        chunk_overlap=50,
    )
    return text_splitter.split_text(text)


def create_embedding(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    try:
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        extra: dict[str, Any] = {"total_exits": len(texts)}
        logger.info("Embeding Created", extra=extra)
        return embeddings
    except Exception:
        logger.exception("Failed to create embeddings")
        raise
