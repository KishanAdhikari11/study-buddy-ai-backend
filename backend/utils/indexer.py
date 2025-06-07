from pinecone import Pinecone
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings, VectorStoreIndex, Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
from typing import Optional, Dict
from core.config import settings

Settings.llm = Gemini(api_key=settings.GOOGLE_API_KEY)
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=settings.GOOGLE_API_KEY)
Settings.chunk_size = 1024
Settings.chunk_overlap = 200

pinecone_client = Pinecone(api_key=settings.PINECONE_API)
index = pinecone_client.Index(settings.PINECONE_INDEX)

def store_markdown_to_vector(markdown_path: str, metadata: Dict = None, user_id: str = None) -> bool:
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        doc = Document(text=content, metadata=metadata or {})
        vector_store = PineconeVectorStore(pinecone_index=index, namespace=user_id or "default")
        pipeline = IngestionPipeline(
            transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=200), Settings.embed_model],
            vector_store=vector_store
        )
        pipeline.run(documents=[doc])
        return True
    except:
        return False

def query_vector_store(query: str, top_k: int = 100, metadata_filter_id: Dict = None, user_id: str = None) -> Optional[str]:
    try:
        vector_store = PineconeVectorStore(pinecone_index=index, namespace=user_id or "default")
        vector_index = VectorStoreIndex.from_vector_store(vector_store)
        query_engine = vector_index.as_query_engine(
            similarity_top_k=top_k,
            filters={"metadata": metadata_filter_id} if metadata_filter_id else None
        )
        response = query_engine.query(query)
        return "\n".join([node.text for node in response.source_nodes]) if response.source_nodes else None
    except:
        return None