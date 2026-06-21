#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

kubectl apply -f "${ROOT_DIR}/kubernetes/manifests"
kubectl -n capstone-ai-platform get pods,svc,ingress,hpa
