# Vector Search Layer

Phase 4 deliverable describing how Postgres and `pgvector` support retrieval.

## Tables

### `documents`

Stores one row per ingested source document.

| Column         | Purpose                        |
| -------------- | ------------------------------ |
| `id`           | Document UUID                  |
| `source_path`  | Local path used for ingestion  |
| `title`        | Human-readable title           |
| `content_hash` | SHA-256 hash for deduplication |
| `metadata`     | Extra JSON metadata            |
| `created_at`   | Ingestion timestamp            |

### `document_chunks`

Stores searchable chunks.

| Column           | Purpose                          |
| ---------------- | -------------------------------- |
| `id`             | Chunk UUID                       |
| `document_id`    | Parent document                  |
| `chunk_index`    | Order within source document     |
| `content`        | Chunk text                       |
| `token_estimate` | Simple whitespace token estimate |
| `embedding`      | `pgvector` embedding column      |
| `metadata`       | Chunk metadata                   |

## Retrieval Query

```sql
SELECT
    c.id AS chunk_id,
    d.title,
    c.chunk_index,
    c.content,
    1 - (c.embedding <=> :query_embedding) AS similarity
FROM document_chunks c
JOIN documents d ON d.id = c.document_id
WHERE 1 - (c.embedding <=> :query_embedding) >= :similarity_threshold
ORDER BY c.embedding <=> :query_embedding
LIMIT :limit;
```

## Index

```sql
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Local Defaults

| Setting              | Default     | Reason                                       |
| -------------------- | ----------- | -------------------------------------------- |
| Embedding provider   | `hash`      | No external model dependency for smoke tests |
| Embedding dimension  | `384`       | Small enough for local testing               |
| Chunk size           | `900` chars | Keeps context focused                        |
| Chunk overlap        | `150` chars | Reduces boundary misses                      |
| Retrieval limit      | `5`         | Enough context without flooding the prompt   |
| Similarity threshold | `0.15`      | Loose default for hash embeddings            |

## Production Improvements

- Use a semantic embedding model rather than hash embeddings.
- Store embedding model name and dimension per document version.
- Add metadata filters for document type, date, owner, or project.
- Add reranking for final context selection.
- Track retrieval evaluations over a fixed question set.
