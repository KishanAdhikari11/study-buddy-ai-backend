from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from core.dependencies import get_vector_store, get_embed_model
import logging

logger = logging.getLogger(__name__)

def index_markdown(markdown_path: str, file_id: str):
    try:
        # Load Markdown file
        documents = SimpleDirectoryReader(input_files=[markdown_path]).load_data()
        if not documents:
            logger.error(f"No documents loaded from {markdown_path}")
            raise ValueError("No content extracted from Markdown")
        
        # Assign file_id as metadata to all documents
        for doc in documents:
            doc.metadata["file_id"] = file_id
            logger.debug(f"Assigned file_id {file_id} to document {doc.id_}")
        
        # Index to Pinecone
        vector_store = get_vector_store()
        embed_model = get_embed_model()
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            embed_model=embed_model
        )
        logger.info(f"Markdown file {markdown_path} indexed with file_id {file_id}")
        
        # Verify vectors in Pinecone
        from pinecone import Pinecone
        pc = Pinecone(api_key=getattr(get_vector_store(), '_pinecone_api_key', None))
        pinecone_index = pc.Index(vector_store._pinecone_index.name)
        stats = pinecone_index.describe_index_stats()
        logger.info(f"Pinecone index stats after indexing: {stats}")
        
        return index
    except Exception as e:
        logger.error(f"Error indexing Markdown: {str(e)}")
        raise