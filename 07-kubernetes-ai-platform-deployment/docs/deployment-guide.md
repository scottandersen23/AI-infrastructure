# Deployment Guide

Phase 7 deliverable for deploying the AI platform stack to a local Kubernetes cluster.

## Prerequisites

- Docker Desktop or compatible container runtime
- `kubectl`
- `kind` or `minikube`
- Optional: `make`

## Local Deployment With kind

### 1. Create the cluster

```bash
cd 07-kubernetes-ai-platform-deployment
bash scripts/create-kind-cluster.sh
```

This creates a local kind cluster with ports `8080` and `8443` mapped for ingress.

### 2. Build local images

The manifests use local image names:

```text
ai-platform/api-service:local
ai-platform/worker-service:local
ai-platform/llm-service:local
ai-platform/observability-service:local
```

Build these from the earlier phase projects, or retag existing images before loading them into kind:

```bash
kind load docker-image ai-platform/api-service:local --name ai-platform
kind load docker-image ai-platform/worker-service:local --name ai-platform
kind load docker-image ai-platform/llm-service:local --name ai-platform
kind load docker-image ai-platform/observability-service:local --name ai-platform
```

### 3. Deploy manifests

```bash
bash scripts/deploy-local.sh
```

### 4. Verify pods

```bash
kubectl -n ai-platform get pods
kubectl -n ai-platform get svc
kubectl -n ai-platform get ingress
kubectl -n ai-platform get hpa
```

### 5. Access services

Option A: port-forward:

```bash
bash scripts/port-forward.sh
```

Option B: ingress:

Add a local hosts entry:

```text
127.0.0.1 ai-platform.local
```

Then call:

```bash
curl http://ai-platform.local:8080/api/health
curl http://ai-platform.local:8080/llm/health
curl http://ai-platform.local:8080/observability/health
```

## Rolling Deployments

Update an image:

```bash
kubectl -n ai-platform set image deployment/api-service \
  api-service=ai-platform/api-service:v2
```

Watch rollout:

```bash
kubectl -n ai-platform rollout status deployment/api-service
```

Rollback:

```bash
kubectl -n ai-platform rollout undo deployment/api-service
```

## Troubleshooting

| Issue               | Command                                           |
| ------------------- | ------------------------------------------------- |
| Pod not starting    | `kubectl -n ai-platform describe pod <pod>`       |
| Crash loop          | `kubectl -n ai-platform logs <pod> --previous`    |
| Service not routing | `kubectl -n ai-platform get endpoints`            |
| Ingress not working | `kubectl -n ingress-nginx get pods`               |
| HPA unknown metrics | Install metrics-server                            |
| Image pull errors   | Load images into kind or set a reachable registry |

## Cleanup

```bash
kind delete cluster --name ai-platform
```
