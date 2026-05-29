#!/usr/bin/env bash
set -euo pipefail

echo "API: http://localhost:8000"
echo "LLM: http://localhost:8001"
echo "Observability: http://localhost:8003"

kubectl -n ai-platform port-forward svc/api-service 8000:80 &
kubectl -n ai-platform port-forward svc/llm-service 8001:80 &
kubectl -n ai-platform port-forward svc/observability-service 8003:80 &

wait
