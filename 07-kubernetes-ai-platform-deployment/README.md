# 07. Kubernetes AI Platform Deployment

Kubernetes deployment layer for Phase 7 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Deploy the AI application stack using Kubernetes concepts: pods, deployments, services, config maps, secrets, ingress, resource limits, rolling deployments, autoscaling, and local clusters.

## Stack

| Layer             | Technology               |
| ----------------- | ------------------------ |
| Local cluster     | kind or minikube         |
| Workloads         | Kubernetes Deployments   |
| Networking        | Services + nginx Ingress |
| Configuration     | ConfigMaps + Secrets     |
| Persistence       | Postgres PVC             |
| Autoscaling       | HorizontalPodAutoscaler  |
| Security baseline | NetworkPolicy            |

## Project Structure

```text
07-kubernetes-ai-platform-deployment/
├── diagrams/
│   └── kubernetes-architecture.md
├── docs/
│   ├── deployment-guide.md
│   └── production-readiness-checklist.md
├── kind/
│   └── kind-cluster.yaml
├── manifests/
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secrets.example.yaml
│   ├── 10-postgres.yaml
│   ├── 11-redis.yaml
│   ├── 20-api-service.yaml
│   ├── 21-worker-service.yaml
│   ├── 22-llm-service.yaml
│   ├── 23-observability-service.yaml
│   ├── 24-dashboard.yaml
│   ├── 30-ingress.yaml
│   ├── 40-autoscaling.yaml
│   └── 50-network-policies.yaml
├── scripts/
│   ├── create-kind-cluster.sh
│   ├── deploy-local.sh
│   └── port-forward.sh
└── README.md
```

## Quick Start

### 1. Create a local cluster

```bash
cd 07-kubernetes-ai-platform-deployment
bash scripts/create-kind-cluster.sh
```

### 2. Deploy the stack

```bash
bash scripts/deploy-local.sh
```

### 3. Verify resources

```bash
kubectl -n ai-platform get pods,svc,ingress,hpa
```

### 4. Access services

Use port-forwarding:

```bash
bash scripts/port-forward.sh
```

Or use ingress after adding `127.0.0.1 ai-platform.local` to `/etc/hosts`:

```bash
curl http://ai-platform.local:8080/api/health
```

## Deliverables

| Deliverable                    | Location                                                                                                               |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Kubernetes manifests           | [manifests/](./manifests/)                                                                                             |
| Local cluster deployment       | [kind/kind-cluster.yaml](./kind/kind-cluster.yaml), [scripts/create-kind-cluster.sh](./scripts/create-kind-cluster.sh) |
| Ingress configuration          | [manifests/30-ingress.yaml](./manifests/30-ingress.yaml)                                                               |
| Autoscaling configuration      | [manifests/40-autoscaling.yaml](./manifests/40-autoscaling.yaml)                                                       |
| Deployment guide               | [docs/deployment-guide.md](./docs/deployment-guide.md)                                                                 |
| Production-readiness checklist | [docs/production-readiness-checklist.md](./docs/production-readiness-checklist.md)                                     |

## Related Projects

- [Phase 4 RAG Document Assistant](../04-rag-document-assistant/README.md)
- [Phase 5 AI Observability Platform](../05-ai-observability-platform/README.md)
- [Phase 6 Inference Performance Lab](../06-inference-performance-lab/README.md)
