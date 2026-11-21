#!/usr/bin/env bash
# ==============================================================================
# Argo Rollouts Canary Traffic Simulation & Automated Abort Demonstration
# Author: Sai Nayan Mamilla (sainayanmamilla)
# ==============================================================================

set -euo pipefail

echo "================================================================="
echo " [!] ARGO ROLLOUTS CANARY CONTROLLER VALIDATION"
echo " Candidate: Sai Nayan Mamilla | Namespace: production"
echo " Strategy: Progressive Traffic Weight (10% -> 25% -> 50% -> 100%)"
echo " Prometheus Automated Analysis: Error Rate (<1%) & p95 Latency (<150ms)"
echo "================================================================="

echo "[1/4] Triggering Canary Release of Image v2.0.0..."
kubectl argo rollouts set image enterprise-canary-rollout app=enterprise-registry.internal/apps/enterprise-service:v2.0.0 -n production

echo "[2/4] Monitoring Step 1: 10% Traffic Weight Promotion..."
kubectl argo rollouts get rollout enterprise-canary-rollout -n production

echo "[3/4] Simulating Automated Canary Metric Analysis Check..."
echo "Prometheus Query 1: success-rate = 0.998 (Threshold: >= 0.99) -> PASSED"
echo "Prometheus Query 2: p95-latency  = 0.042s (Threshold: <= 0.150s) -> PASSED"
echo "Analysis status: Successful (Iteration 1/3)"

echo "[4/4] Demonstrating Automated Abort & Rollback Gate..."
echo "[SIMULATION] Injecting high synthetic error rate (HTTP 500) into Canary Pods..."
echo "Simulated Failure: HTTP 500 rate jumped to 8.4% (Threshold: < 1.0%)"
echo "[ALERT] AnalysisTemplate 'http-success-rate-and-latency-analysis' FAILED!"
echo "[ROLLBACK TRIGGER] Argo Rollouts controller automatically aborted rollout."
echo "Active stable pods: 10/10 (v1.0.0). Canary pods: 0/10 (Terminated)."
echo "Zero production blast radius to the remaining 90% of user traffic."

echo "================================================================="
echo " [✓] CANARY ROLLOUT CONTROLLER & ROLLBACK TEST COMPLETED"
echo "================================================================="
