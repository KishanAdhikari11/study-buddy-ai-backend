from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    texts: list[str]


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
