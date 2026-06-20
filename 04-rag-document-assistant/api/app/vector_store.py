import json
import uuid
from typing import Any

from api.app.chunking import TextChunk
from api.app.database import get_connection
from api.app.embeddings import to_vector_literal
from api.app.schemas import DocumentSummary, RetrievedChunk


def upsert_document(
    source_path: str,
    title: str,
    content_hash: str,
    metadata: dict[str, Any],
    chunks: list[TextChunk],
    embeddings: list[list[float]],
) -> tuple[uuid.UUID, int]:
    document_id = uuid.uuid4()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM documents
                WHERE content_hash = %s
                RETURNING id;
                """,
                (content_hash,),
            )
            cursor.execute(
                """
                INSERT INTO documents (id, source_path, title, content_hash, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb);
                """,
                (
                    document_id,
                    source_path,
                    title,
                    content_hash,
                    json.dumps(metadata),
                ),
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        id,
                        document_id,
                        chunk_index,
                        content,
                        token_estimate,
                        embedding,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb);
                    """,
                    (
                        uuid.uuid4(),
                        document_id,
                        chunk.index,
                        chunk.content,
                        chunk.token_estimate,
                        to_vector_literal(embedding),
                        json.dumps({"chunk_index": chunk.index}),
                    ),
                )

    return document_id, len(chunks)


def search_chunks(
    query_embedding: list[float],
    limit: int,
    similarity_threshold: float,
) -> list[RetrievedChunk]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Exact scans behave predictably for tiny local learning datasets.
            cursor.execute("SET LOCAL enable_indexscan = off;")
            cursor.execute(
                """
                SELECT
                    c.id AS chunk_id,
                    c.document_id,
                    d.title,
                    d.source_path,
                    c.chunk_index,
                    c.content,
                    c.metadata,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE 1 - (c.embedding <=> %s::vector) >= %s
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s::int;
                """,
                (
                    to_vector_literal(query_embedding),
                    to_vector_literal(query_embedding),
                    similarity_threshold,
                    to_vector_literal(query_embedding),
                    limit,
                ),
            )
            rows = cursor.fetchall()

    return [
        RetrievedChunk(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            title=row["title"],
            source_path=row["source_path"],
            chunk_index=row["chunk_index"],
            content=row["content"],
            similarity=round(float(row["similarity"]), 4),
            metadata=row["metadata"] or {},
        )
        for row in rows
    ]


def list_documents() -> list[DocumentSummary]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.title,
                    d.source_path,
                    d.content_hash,
                    d.created_at,
                    count(c.id)::int AS chunk_count
                FROM documents d
                LEFT JOIN document_chunks c ON c.document_id = d.id
                GROUP BY d.id
                ORDER BY d.created_at DESC;
                """
            )
            rows = cursor.fetchall()

    return [DocumentSummary(**row) for row in rows]
