# Production-Readiness Checklist

Phase 7 deliverable for evaluating whether the Kubernetes AI platform is ready to move beyond a local cluster.

## Deployment Safety

- [ ] Images are pinned by immutable digest, not `latest`.
- [ ] Rolling updates use readiness probes and `maxUnavailable: 0` for user-facing services.
- [ ] Rollback procedure is documented and tested.
- [ ] Database migrations run as controlled jobs, not inside app startup.
- [ ] Resource requests and limits are set for every container.

## Security

- [ ] Secrets are managed by a real secret manager or sealed secrets.
- [ ] Example secrets are not deployed in production.
- [ ] Network policies restrict service-to-service traffic.
- [ ] Ingress uses TLS and trusted certificates.
- [ ] API authentication and authorization are enabled.
- [ ] Container images are scanned for vulnerabilities.
- [ ] Pods run as non-root where supported.

## Reliability

- [ ] Liveness and readiness probes exist for every HTTP service.
- [ ] Horizontal Pod Autoscalers are configured for stateless services.
- [ ] Persistent services have backup and restore plans.
- [ ] Redis queue durability requirements are documented.
- [ ] Postgres storage class, volume size, and retention are production appropriate.
- [ ] Pod disruption budgets are defined for critical services.

## Observability

- [ ] Logs are centralized and searchable.
- [ ] Metrics cover request latency, error rate, token usage, retrieval latency, and queue depth.
- [ ] OpenTelemetry traces propagate across API, worker, LLM, and RAG services.
- [ ] Dashboards exist for service health and AI reliability.
- [ ] Alerts are configured for saturation, errors, and unavailable dependencies.

## AI-Specific Readiness

- [ ] Model runtime memory and GPU requirements are known.
- [ ] LLM service has concurrency limits and backpressure.
- [ ] RAG retrieval quality is evaluated with a fixed test set.
- [ ] Prompt templates are versioned.
- [ ] Model and embedding versions are tracked.
- [ ] Token budgets are enforced.

## Local-to-Production Gaps

| Local Lab Choice        | Production Replacement                                          |
| ----------------------- | --------------------------------------------------------------- |
| Example Secret manifest | External Secrets / sealed-secrets / cloud secret manager        |
| Single Postgres pod     | Managed Postgres or HA operator                                 |
| Mock LLM service        | GPU-backed model serving runtime                                |
| Basic nginx ingress     | Managed ingress/load balancer with TLS                          |
| CPU/memory HPA          | Custom metrics HPA for queue depth, latency, or GPU utilization |
| Local dashboard         | Managed Grafana/Phoenix/Prometheus stack                        |
