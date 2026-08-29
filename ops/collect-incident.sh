#!/usr/bin/env bash

set -e

NAMESPACE="kube-ai-guardian"
APP="guardian-api"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
OUTDIR="incidents/$TIMESTAMP"

mkdir -p "$OUTDIR"

kubectl get pods -n "$NAMESPACE" -o wide > "$OUTDIR/pods.txt"
kubectl get events -n "$NAMESPACE" --sort-by=.lastTimestamp > "$OUTDIR/events.txt"
kubectl describe deployment "$APP" -n "$NAMESPACE" > "$OUTDIR/deployment.txt"
kubectl logs deployment/"$APP" -n "$NAMESPACE" --tail=200 > "$OUTDIR/logs.txt" 2>&1
kubectl rollout history deployment/"$APP" -n "$NAMESPACE" > "$OUTDIR/rollout-history.txt"

echo "Incident evidence saved to: $OUTDIR"
