# AI Reliability Report

Phase 5 deliverable for documenting reliability risks, metrics, and operating practices for AI APIs.

## Reliability Goals

| Goal                    | Signal                                               |
| ----------------------- | ---------------------------------------------------- |
| Fast enough for users   | Request latency and model latency stay within target |
| Grounded answers        | Retrieval hit rate and source count remain high      |
| Predictable model usage | Token counts do not spike unexpectedly               |
| Clear failures          | Errors are captured with trace context               |
| Measurable quality      | Quality score trends are visible over time           |

## Core Metrics

| Metric             | Current Implementation               | Production Target                        |
| ------------------ | ------------------------------------ | ---------------------------------------- |
| Request latency    | Captured per `/ask` request          | p50/p95/p99 by route and model           |
| Model latency      | Captured in `ai.model.generate` span | Track by model, prompt size, output size |
| Retrieval latency  | Captured in `ai.retrieval` span      | Track by vector store, index, filters    |
| Token count        | Prompt, completion, total            | Budget alerts and anomaly detection      |
| Error rate         | Stored in local metrics DB           | Alert by route/model/error type          |
| Retrieval hit rate | Boolean per request                  | Evaluate against labeled question set    |
| Quality score      | Local heuristic                      | Replace with eval suite and human review |

## Trace Design

Each request emits nested spans:

```text
POST /ask
  -> ai.request
      -> ai.retrieval
      -> ai.model.generate
      -> ai.quality.evaluate
```

This span layout makes it clear whether user-visible latency comes from API overhead, retrieval, model generation, or evaluation.

## Failure Modes

| Failure             | Detection Signal            | Response                                             |
| ------------------- | --------------------------- | ---------------------------------------------------- |
| Model runtime slow  | High `ai.model.latency_ms`  | Reduce model size, enable streaming, scale serving   |
| Retrieval degraded  | Low retrieval hit rate      | Reindex documents, tune chunking, improve embeddings |
| Prompt too large    | Token count spike           | Add context compression, lower retrieved chunk count |
| Model exception     | Error span and error metric | Retry safe failures, surface fallback response       |
| Poor answer quality | Quality score drops         | Run eval set, inspect prompt/context, add guardrails |

## Suggested SLOs

| SLO                   | Initial Target                                    |
| --------------------- | ------------------------------------------------- |
| `/ask` availability   | 99% successful responses locally during test runs |
| p95 request latency   | Under 2 seconds for mock pipeline                 |
| p95 retrieval latency | Under 250 ms for local retrieval                  |
| p95 model latency     | Under 1.5 seconds for local model calls           |
| Retrieval hit rate    | Above 90% on known-answer questions               |
| Error rate            | Below 1% during steady-state runs                 |

## Operational Checklist

1. Verify `/health` before test runs.
2. Send a known set of questions through `/ask`.
3. Inspect `/dashboard` for latency, tokens, errors, and quality.
4. Open Phoenix and inspect trace waterfall timing.
5. Investigate any request where model latency, retrieval latency, or token usage is an outlier.
6. Update prompts, chunking, or model configuration based on recurring failures.

## Next Improvements

- Add Prometheus counters and histograms for production-style scraping.
- Replace the local quality heuristic with an eval set.
- Add trace attributes for prompt template version and retrieval index version.
- Add alerting thresholds for latency, errors, and token spikes.
- Connect the Phase 4 RAG API directly and trace real retrieval calls.
