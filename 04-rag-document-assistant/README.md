# 04. RAG Document Assistant

Markdown/PDF document assistant backed by Postgres and `pgvector` for Phase 4 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Build a retrieval-augmented generation system over local documents using Postgres as the vector store.

## Stack

| Layer            | Technology                                                           |
| ---------------- | -------------------------------------------------------------------- |
| API              | FastAPI + Uvicorn                                                    |
| Vector store     | Postgres 16 + pgvector                                               |
| Document loading | Markdown, text, PDF                                                  |
| Chunking         | Overlapping text chunks                                              |
| Embeddings       | Deterministic hash embeddings by default, optional Ollama embeddings |
| Generation       | Optional Phase 3 local LLM API via `LLM_API_URL`                     |
| Orchestration    | Docker Compose                                                       |

## Project Structure

```text
04-rag-document-assistant/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI routes
│       ├── database.py          # pgvector schema initialization
│       ├── document_loader.py   # Markdown/text/PDF loading
│       ├── chunking.py          # Overlapping chunking
│       ├── embeddings.py        # Hash + Ollama embedding providers
│       ├── vector_store.py      # pgvector writes and similarity search
│       ├── rag.py               # Retrieval + answer generation
│       ├── prompts.py           # Runtime prompt builder
│       └── schemas.py           # API models
├── docs/
│   ├── retrieval-quality-notes.md
│   └── vector-search-layer.md
├── prompts/
│   ├── query-rewrite-template.md
│   └── rag-answer-template.md
├── sample-docs/
│   └── ai-infrastructure-overview.md
├── scripts/
│   └── ingest.py
├── sql/
│   └── init.sql
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### 1. Start Postgres + API

```bash
cd 04-rag-document-assistant
docker compose up --build
```

The API runs at `http://localhost:8002`.

### 2. Check Health

```bash
curl -s http://localhost:8002/health | python3 -m json.tool
```

Expected:

```json
{
  "status": "ok",
  "postgres": "ok",
  "vector_extension": "ok",
  "embedding_provider": "hash"
}
```

### 3. Ingest the Sample Document

From the host, use the API endpoint with the path inside the container:

```bash
curl -s -X POST http://localhost:8002/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{"path":"/app/sample-docs/ai-infrastructure-overview.md","title":"AI Infrastructure Overview"}' \
  | python3 -m json.tool
```

### 4. Search Retrieved Chunks

```bash
curl -s -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Why use Postgres with pgvector for RAG?","limit":3}' \
  | python3 -m json.tool
```

### 5. Ask a RAG Question

```bash
curl -s -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"How does RAG improve answer grounding?","limit":3}' \
  | python3 -m json.tool
```

Without `LLM_API_URL`, `/ask` returns retrieved sources plus a placeholder answer. Set `LLM_API_URL=http://host.docker.internal:8001` to connect this project to the Phase 3 local LLM wrapper.

## API Endpoints

| Endpoint                 | Purpose                                        |
| ------------------------ | ---------------------------------------------- |
| `GET /health`            | Verify Postgres and pgvector availability      |
| `POST /documents/ingest` | Ingest Markdown, text, or PDF documents        |
| `GET /documents`         | List indexed documents and chunk counts        |
| `POST /search`           | Return relevant chunks from pgvector           |
| `POST /ask`              | Retrieve context and generate/source an answer |
| `GET /docs`              | Swagger UI                                     |

## Configuration

| Variable                 | Default                                   | Description                                    |
| ------------------------ | ----------------------------------------- | ---------------------------------------------- |
| `DATABASE_URL`           | `postgresql://rag:rag@localhost:5433/rag` | Postgres connection string                     |
| `EMBEDDING_PROVIDER`     | `hash`                                    | `hash` or `ollama`                             |
| `EMBEDDING_DIMENSION`    | `384`                                     | pgvector column dimension                      |
| `OLLAMA_BASE_URL`        | `http://localhost:11434`                  | Ollama URL for embedding provider              |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text`                        | Ollama embedding model                         |
| `LLM_API_URL`            | empty                                     | Optional Phase 3 API URL for answer generation |
| `CHUNK_SIZE`             | `900`                                     | Character target for chunks                    |
| `CHUNK_OVERLAP`          | `150`                                     | Character overlap between chunks               |
| `RETRIEVAL_LIMIT`        | `5`                                       | Default retrieved chunk count                  |
| `SIMILARITY_THRESHOLD`   | `0.15`                                    | Minimum similarity score                       |

## Using Ollama Embeddings

The default hash embeddings are intentionally simple so the system can run without model downloads. For stronger semantic retrieval:

```bash
ollama pull nomic-embed-text
EMBEDDING_PROVIDER=ollama EMBEDDING_DIMENSION=768 docker compose up --build
```

If you change `EMBEDDING_DIMENSION`, reset the database volume:

```bash
docker compose down -v
docker compose up --build
```

## Deliverables

| Deliverable                     | Location                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------- |
| Markdown/PDF document assistant | `api/app/document_loader.py`, `POST /documents/ingest`                                  |
| RAG API endpoint                | `POST /ask` in `api/app/main.py`                                                        |
| Vector search layer             | `api/app/vector_store.py`, [docs/vector-search-layer.md](./docs/vector-search-layer.md) |
| Retrieval quality notes         | [docs/retrieval-quality-notes.md](./docs/retrieval-quality-notes.md)                    |
| Prompt template examples        | [prompts/](./prompts/)                                                                  |

## Related Projects

- [Phase 3 Local LLM Serving Lab](../03-local-llm-serving-lab/README.md)
- [RAG Answer Prompt Template](./prompts/rag-answer-template.md)
- [Vector Search Layer](./docs/vector-search-layer.md)
