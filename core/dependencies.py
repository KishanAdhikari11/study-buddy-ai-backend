import logging

from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from core.settings import settings

logger = logging.getLogger(__name__)


def get_pinecone_client():
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        logger.info("Pinecone client initialized")
        return pc
    except Exception as e:
        logger.error("Failed to initialize Pinecone client", exc_info=e)
        raise


def get_llm():
    try:
        llm = Gemini(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini LLM initialized")
        return llm
    except Exception as e:
        logger.error("Failed to initialize Gemini LLM", exc_info=e)
        raise


def get_embed_model():
    try:
        embed_model = GeminiEmbedding(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini embedding model initialized")
        return embed_model
    except Exception as e:
        logger.error("Failed to initialize Gemini embedding model", exc_info=e)
        raise


def get_vector_store():
    try:
        pinecone_client = get_pinecone_client()
        vector_store = PineconeVectorStore(
            pinecone_index=pinecone_client.Index(settings.PINECONE_INDEX_NAME),
            namespace="pdf_quizzes",
        )
        logger.info(
            "Vector store initialized for index",
            extra={"index_name": settings.PINECONE_INDEX_NAME},
        )
        return vector_store
    except Exception as e:
        logger.error("Failed to initialize vector store", exc_info=e)
        raise
