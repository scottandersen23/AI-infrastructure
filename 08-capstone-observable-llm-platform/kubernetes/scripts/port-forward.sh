#!/usr/bin/env bash
set -euo pipefail

kubectl -n capstone-ai-platform port-forward svc/api-gateway 8010:80 &
kubectl -n capstone-ai-platform port-forward svc/llm-service 8011:80 &
kubectl -n capstone-ai-platform port-forward svc/rag-service 8012:80 &
kubectl -n capstone-ai-platform port-forward svc/observability 8013:80 &

wait
