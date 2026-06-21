from fastapi import FastAPI

from app.retrieval import load_chunks, search
from app.schemas import HealthResponse, SearchRequest, SearchResponse


app = FastAPI(
    title="Capstone RAG Service",
    description="Deterministic document retrieval service for the capstone platform.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        embedding_provider="hash",
        indexed_chunks=len(load_chunks()),
    )


@app.post("/search", response_model=SearchResponse, tags=["Retrieval"])
async def search_documents(request: SearchRequest) -> SearchResponse:
    return SearchResponse(
        query=request.query,
        results=search(request.query, request.limit),
    )
