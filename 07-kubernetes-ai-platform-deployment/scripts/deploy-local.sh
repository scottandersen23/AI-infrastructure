#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/01-configmap.yaml
kubectl apply -f manifests/02-secrets.example.yaml
kubectl apply -f manifests/

kubectl -n ai-platform rollout status deployment/postgres
kubectl -n ai-platform rollout status deployment/redis
kubectl -n ai-platform rollout status deployment/api-service
kubectl -n ai-platform rollout status deployment/llm-service
kubectl -n ai-platform rollout status deployment/observability-service

kubectl -n ai-platform get pods,svc,ingress,hpa
