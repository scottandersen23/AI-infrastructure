from pathlib import Path
from typing import Any

from api.app.chunking import chunk_text
from api.app.config import settings
from api.app.document_loader import load_document
from api.app.embeddings import get_embedding_provider
from api.app.schemas import IngestResponse
from api.app.vector_store import upsert_document


async def ingest_document(
    path: str,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> IngestResponse:
    source_path, text, content_hash = load_document(path)
    chunks = chunk_text(
        text=text,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    provider = get_embedding_provider()
    embeddings = [await provider.embed(chunk.content) for chunk in chunks]

    resolved_title = title or Path(source_path).stem.replace("-", " ").replace("_", " ")
    document_id, chunks_created = upsert_document(
        source_path=source_path,
        title=resolved_title,
        content_hash=content_hash,
        metadata=metadata or {},
        chunks=chunks,
        embeddings=embeddings,
    )

    return IngestResponse(
        document_id=document_id,
        title=resolved_title,
        source_path=source_path,
        chunks_created=chunks_created,
        content_hash=content_hash,
    )
