# 03. Local LLM Serving Lab

Local model serving lab for Phase 3 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Understand how local LLM inference works by running, wrapping, streaming, and benchmarking local models.

## Stack

| Layer              | Technology                            |
| ------------------ | ------------------------------------- |
| API wrapper        | FastAPI + Uvicorn                     |
| Default runtime    | Ollama HTTP API                       |
| Smoke-test runtime | Built-in mock runtime                 |
| Benchmarking       | Python + httpx                        |
| Docs               | Markdown reports and Mermaid diagrams |
| Optional container | Docker Compose                        |

## Project Structure

```text
03-local-llm-serving-lab/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI routes
│       ├── runtime_clients.py   # Ollama + mock runtime clients
│       ├── schemas.py           # Request/response models
│       └── config.py            # Environment configuration
├── diagrams/
│   └── serving-flow.md
├── docs/
│   ├── benchmark-results.md
│   ├── latency-throughput-report.md
│   └── model-comparison-notes.md
├── scripts/
│   └── benchmark.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.12+
- Optional: [Ollama](https://ollama.com/) for real local model inference
- Optional: Docker Desktop for containerized API wrapper

## Quick Start

### 1. Install dependencies

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

### 2. Smoke test with the mock runtime

```bash
LLM_RUNTIME=mock uvicorn api.app.main:app --reload --port 8001
```

In another terminal:

```bash
curl -s http://localhost:8001/health | python3 -m json.tool
curl -s -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain local LLM serving in one paragraph."}' \
  | python3 -m json.tool
```

### 3. Run with Ollama

Install and start Ollama, then pull a small baseline model:

```bash
ollama pull llama3.2:3b
ollama serve
```

Start the API wrapper:

```bash
LLM_RUNTIME=ollama \
OLLAMA_BASE_URL=http://localhost:11434 \
DEFAULT_MODEL=llama3.2:3b \
uvicorn api.app.main:app --reload --port 8001
```

### 4. Test streaming

```bash
curl -N -X POST http://localhost:8001/generate/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Stream a short explanation of quantization.","max_tokens":120}'
```

### 5. Run benchmarks

```bash
python scripts/benchmark.py \
  --api-url http://localhost:8001 \
  --models llama3.2:3b \
  --requests 3 \
  --max-tokens 128
```

Benchmark JSON and CSV outputs are written to `benchmark-runs/`.

## API Endpoints

| Endpoint                | Purpose                               |
| ----------------------- | ------------------------------------- |
| `GET /health`           | Check wrapper and runtime status      |
| `GET /models`           | List locally available runtime models |
| `POST /generate`        | Generate a non-streaming response     |
| `POST /generate/stream` | Stream generated text chunks          |
| `GET /docs`             | Swagger UI                            |
| `GET /redoc`            | ReDoc                                 |

## Request Example

```json
{
  "model": "llama3.2:3b",
  "prompt": "Explain CPU vs GPU inference for local LLMs.",
  "temperature": 0.2,
  "max_tokens": 180
}
```

## Runtime Configuration

| Variable                  | Default                  | Description                                         |
| ------------------------- | ------------------------ | --------------------------------------------------- |
| `LLM_RUNTIME`             | `ollama`                 | `ollama` for real inference, `mock` for smoke tests |
| `OLLAMA_BASE_URL`         | `http://localhost:11434` | Ollama API base URL                                 |
| `DEFAULT_MODEL`           | `llama3.2:3b`            | Model used when requests omit `model`               |
| `REQUEST_TIMEOUT_SECONDS` | `120`                    | Non-streaming request timeout                       |

## Docker Compose

Docker Compose runs only the API wrapper. Ollama still runs on the host by default.

```bash
docker compose up --build
```

For a container-only smoke test:

```bash
LLM_RUNTIME=mock docker compose up --build
```

## Deliverables

| Deliverable                   | Location                                                                         |
| ----------------------------- | -------------------------------------------------------------------------------- |
| Local LLM API wrapper         | `api/app/`                                                                       |
| Streaming response endpoint   | `POST /generate/stream` in `api/app/main.py`                                     |
| Model comparison notes        | [docs/model-comparison-notes.md](./docs/model-comparison-notes.md)               |
| Benchmark results             | [docs/benchmark-results.md](./docs/benchmark-results.md), `scripts/benchmark.py` |
| Latency and throughput report | [docs/latency-throughput-report.md](./docs/latency-throughput-report.md)         |

## Learning Notes

- Tokenization affects prompt-processing latency and context-window cost.
- Streaming improves perceived latency even when total generation time is unchanged.
- Quantization changes the memory, speed, and quality balance.
- Throughput numbers should be interpreted with prompt length and hardware notes.

## Related Projects

- [Phase 2 Backend API + Async Worker System](../02-backend-api-worker/README.md)
- [Serving Flow Diagram](./diagrams/serving-flow.md)
