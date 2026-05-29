#!/usr/bin/env bash
set -euo pipefail

kind create cluster --config kind/kind-cluster.yaml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo "Waiting for ingress-nginx controller..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s

echo "Cluster ready. Add this host entry if needed:"
echo "127.0.0.1 ai-platform.local"
