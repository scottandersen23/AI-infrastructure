# Capstone Production-Readiness Checklist

## Deployment Safety

- [ ] Images are pinned by immutable digest.
- [ ] Rollbacks are tested for API, worker, RAG, LLM, and observability services.
- [ ] Database migrations run as controlled jobs.
- [ ] Readiness and liveness probes exist for HTTP services.
- [ ] Resource requests and limits are set for every workload.

## AI Reliability

- [ ] Retrieval quality is evaluated with a fixed question set.
- [ ] Prompt templates are versioned.
- [ ] Model and embedding versions are tracked.
- [ ] Token budgets are enforced at the gateway.
- [ ] LLM concurrency limits and backpressure are configured.

## Observability

- [ ] Request latency, model latency, retrieval latency, token usage, and errors are tracked.
- [ ] Trace propagation exists across API, RAG, LLM, and worker boundaries.
- [ ] Dashboard panels cover p95 latency, error rate, retrieval hit rate, and queue depth.
- [ ] Alerts exist for dependency failures and saturation.

## Security

- [ ] Secrets come from a managed secret store.
- [ ] Ingress uses TLS.
- [ ] API authentication and authorization are implemented.
- [ ] Network policies restrict service-to-service traffic.
- [ ] Container images are scanned.

## Production Replacements

| Local Choice        | Production Replacement                                          |
| ------------------- | --------------------------------------------------------------- |
| SQLite metrics      | Managed metrics store or telemetry backend                      |
| Mock LLM            | GPU-backed model serving or managed inference                   |
| Single Postgres pod | Managed Postgres or HA operator                                 |
| Basic Redis         | Managed Redis with persistence requirements                     |
| CPU HPA             | Custom metrics HPA for latency, queue depth, or GPU utilization |
