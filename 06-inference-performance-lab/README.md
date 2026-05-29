# 06. Inference Performance Lab

Model-serving performance lab for Phase 6 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Understand why AI systems become slow and how to measure performance bottlenecks across latency, throughput, batching, concurrency, KV cache pressure, quantization, and hardware limits.

## Stack

| Layer              | Technology             |
| ------------------ | ---------------------- |
| Mock inference API | FastAPI + Uvicorn      |
| Load testing       | Async Python + httpx   |
| Analysis           | Python summary scripts |
| Reports            | Markdown               |
| Diagrams           | Mermaid                |
| Optional container | Docker Compose         |

## Project Structure

```text
06-inference-performance-lab/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI routes
│       ├── inference.py     # Mock model-serving simulator
│       ├── schemas.py       # Request/response models
│       └── config.py        # Performance knobs
├── diagrams/
│   └── performance-architecture.md
├── docs/
│   ├── before-after-optimization-notes.md
│   ├── bottleneck-analysis.md
│   ├── load-test-results.md
│   └── model-serving-benchmark-report.md
├── scripts/
│   ├── analyze_results.py
│   └── load_test.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
cd 06-inference-performance-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

### 2. Start the inference API

```bash
uvicorn api.app.main:app --reload --port 8004
```

Or with Docker:

```bash
docker compose up --build
```

### 3. Run a single request

```bash
curl -s -X POST http://localhost:8004/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain batching for model serving.","max_tokens":128}' \
  | python3 -m json.tool
```

### 4. Run a load test

```bash
python scripts/load_test.py \
  --api-url http://localhost:8004 \
  --concurrency 4 \
  --requests 16 \
  --max-tokens 128
```

### 5. Analyze a result file

```bash
python scripts/analyze_results.py results/load-test-YYYYMMDDTHHMMSSZ.json
```

## API Endpoints

| Endpoint         | Purpose                                            |
| ---------------- | -------------------------------------------------- |
| `GET /health`    | Show model and concurrency settings                |
| `POST /generate` | Simulate model inference and return timing metrics |
| `GET /docs`      | Swagger UI                                         |

## Performance Knobs

| Variable                  | Default                | Description                                  |
| ------------------------- | ---------------------- | -------------------------------------------- |
| `MODEL_NAME`              | `mock-inference-model` | Model label in responses                     |
| `BASE_TOKEN_LATENCY_MS`   | `18`                   | Simulated decode latency per generated token |
| `PROMPT_TOKEN_LATENCY_MS` | `1.5`                  | Simulated prefill latency per prompt token   |
| `MAX_CONCURRENT_REQUESTS` | `4`                    | Concurrent inference slots before queueing   |
| `SIMULATED_VRAM_MB`       | `4096`                 | Memory limit used for estimates              |
| `KV_CACHE_MB_PER_TOKEN`   | `0.02`                 | Simulated KV cache memory per token          |

## Deliverables

| Deliverable                      | Location                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------ |
| Load test results                | [docs/load-test-results.md](./docs/load-test-results.md), `scripts/load_test.py`           |
| Model-serving benchmark report   | [docs/model-serving-benchmark-report.md](./docs/model-serving-benchmark-report.md)         |
| Bottleneck analysis              | [docs/bottleneck-analysis.md](./docs/bottleneck-analysis.md), `scripts/analyze_results.py` |
| Before/after optimization notes  | [docs/before-after-optimization-notes.md](./docs/before-after-optimization-notes.md)       |
| Performance architecture diagram | [diagrams/performance-architecture.md](./diagrams/performance-architecture.md)             |

## Related Projects

- [Phase 3 Local LLM Serving Lab](../03-local-llm-serving-lab/README.md)
- [Phase 5 AI Observability Platform](../05-ai-observability-platform/README.md)
