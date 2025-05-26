from pinecone import Pinecone
from dotenv import load_dotenv
import os
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.vector_stores import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
load_dotenv()


llm=Gemini()
embedding_model=GeminiEmbedding(model_name="models/embedding-001")
Settings.llm=llm
Settings.embed_model=embedding_model
Settings.chunk_size=1024
pinecone_api=os.getenv("PINECONE_API")
pinecone_client=Pinecone(api_key=pinecone_api)


pinecone_index_name = os.getenv("PINECONE_INDEX", "study-buddy")
index = pinecone_client.Index(pinecone_index_name)

vector_store = PineconeVectorStore(pinecone_index=index)
index = VectorStoreIndex.from_vector_store(vector_store)

node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)


def store_markdown_to_vector(md:str):
    doc=Document(text=md)
    pipeline=IngestionPipeline(
        transformations=[node_parser,embedding_model],
        vector_store=vector_store
    )
    pipeline.run(documents=[doc])
    print("Markdown content stored in vector DB")
    
    
    