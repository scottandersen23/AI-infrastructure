# Performance Architecture Diagram

Phase 6 deliverable for visualizing model-serving performance measurement.

## Component Diagram

```mermaid
flowchart TB
    Tester[Load Test Script]
    Client[HTTP Client Pool]
    API[Inference API]
    Queue[Concurrency Gate / Queue]
    Prefill[Prompt Evaluation / Prefill]
    Decode[Token Generation / Decode]
    Metrics[Result Metrics]
    Reports[Benchmark + Bottleneck Reports]

    Tester --> Client
    Client -->|concurrent POST /generate| API
    API --> Queue
    Queue --> Prefill
    Prefill --> Decode
    Decode --> API
    API --> Client
    Client --> Metrics
    Metrics --> Reports
```

## Timing Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Load as Load Tester
    participant API as Inference API
    participant Queue as Queue / Semaphore
    participant Model as Model Runtime

    Load->>API: POST /generate
    API->>Queue: Wait for inference slot
    Queue-->>API: Slot acquired
    API->>Model: Prompt prefill
    Model-->>API: Prompt evaluated
    API->>Model: Decode tokens
    Model-->>API: Generated text
    API-->>Load: Response + timing metrics
```

## Bottleneck Map

```text
High queue_wait_ms
  -> concurrency saturation
  -> add replicas, lower request size, tune batching

High prompt_eval_ms
  -> long context or slow prefill
  -> reduce chunks, compress context, tune prefill batch

High generation_ms
  -> decode-bound model runtime
  -> quantize, smaller model, GPU acceleration, batching

High estimated_vram_mb
  -> KV cache pressure
  -> lower context, lower concurrency, use paged attention
```
