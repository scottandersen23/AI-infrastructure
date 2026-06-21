from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5_000)
    limit: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    title: str
    chunk_index: int
    similarity: float
    content: str


class SearchResponse(BaseModel):
    query: str
    results: list[Source]


class HealthResponse(BaseModel):
    status: str
    embedding_provider: str
    indexed_chunks: int
