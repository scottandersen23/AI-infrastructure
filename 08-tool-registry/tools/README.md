# Built-in Tool Catalog

Initial tools seeded in `sql/init.sql` and implemented as stubs in `executor/app/handlers/`.

## search_docs

Retrieve relevant document chunks for a user query.

| Field   | Type    | Required | Description        |
| ------- | ------- | -------- | ------------------ |
| `query` | string  | yes      | Search query       |
| `limit` | integer | no       | Max results (1–20) |

**Integration target:** Phase 1 RAG service (`RAG_SERVICE_URL`, default capstone `:8012`)

## get_metrics

Return aggregate AI platform reliability metrics.

| Field    | Type | Required | Description  |
| -------- | ---- | -------- | ------------ |
| _(none)_ |      |          | Empty object |

**Integration target:** Capstone observability service (`METRICS_URL`, default `:8013`)

## get_job_status

Look up async job status by ID.

| Field    | Type   | Required | Description          |
| -------- | ------ | -------- | -------------------- |
| `job_id` | string | yes      | Async job identifier |

**Integration target:** Capstone API gateway (`JOBS_API_URL`, default `:8010`)

## LLM Binding Format

Tools are exposed to LLMs in OpenAI-compatible function calling shape:

```json
{
  "type": "function",
  "function": {
    "name": "search_docs",
    "description": "Search indexed documents and return relevant source chunks.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": { "type": "string", "description": "Search query" },
        "limit": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20,
          "default": 5
        }
      },
      "required": ["query"]
    }
  }
}
```

Project 09 will consume `GET /tools` from the registry API to bind these schemas to the agent runtime.
