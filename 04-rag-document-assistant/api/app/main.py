from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from psycopg import Error as PsycopgError

from api.app.config import settings
from api.app.database import get_connection, init_db
from api.app.ingestion import ingest_document
from api.app.rag import answer_question, retrieve
from api.app.schemas import (
    AskRequest,
    AskResponse,
    DocumentSummary,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
)
from api.app.vector_store import list_documents


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RAG Document Assistant",
    description="Markdown/PDF assistant backed by Postgres and pgvector.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    postgres_status = "ok"
    vector_status = "ok"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                if cursor.fetchone() is None:
                    vector_status = "missing"
    except PsycopgError:
        postgres_status = "error"
        vector_status = "unknown"

    return HealthResponse(
        status="ok" if postgres_status == "ok" and vector_status == "ok" else "degraded",
        postgres=postgres_status,
        vector_extension=vector_status,
        embedding_provider=settings.embedding_provider,
    )


@app.post("/documents/ingest", response_model=IngestResponse, tags=["Documents"])
async def ingest(request: IngestRequest) -> IngestResponse:
    try:
        return await ingest_document(
            path=request.path,
            title=request.title,
            metadata=request.metadata,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.get("/documents", response_model=list[DocumentSummary], tags=["Documents"])
async def documents() -> list[DocumentSummary]:
    return list_documents()


@app.post("/search", response_model=SearchResponse, tags=["Retrieval"])
async def search(request: SearchRequest) -> SearchResponse:
    threshold = request.similarity_threshold or settings.similarity_threshold
    results = await retrieve(
        query=request.query,
        limit=request.limit,
        similarity_threshold=threshold,
    )
    return SearchResponse(query=request.query, results=results)


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask(request: AskRequest) -> AskResponse:
    threshold = request.similarity_threshold or settings.similarity_threshold
    try:
        return await answer_question(
            question=request.query,
            limit=request.limit,
            similarity_threshold=threshold,
            include_context=request.include_context,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG generation failed: {exc}",
        ) from exc
