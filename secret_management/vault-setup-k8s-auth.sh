#!/usr/bin/env bash
# ==============================================================================
# Enterprise Secret Management: Vault & Kubernetes Integration Suite
# Author: Sai Nayan Mamilla (sainayanmamilla)
# ==============================================================================

set -euo pipefail

export VAULT_ADDR="${VAULT_ADDR:-http://vault.vault-system.svc.cluster.local:8200}"

echo "================================================================="
echo " [!] HASHICORP VAULT ENTERPRISE SECRET ORCHESTRATION"
echo " Operator: Sai Nayan Mamilla | Host: Sais-MacBook-Pro.local"
echo " Vault Server: ${VAULT_ADDR}"
echo "================================================================="

echo "[1/5] Enabling KV Version 2 Secret Engine..."
vault secrets enable -path=secret kv-v2 || echo "KV-v2 engine already enabled."

echo "[2/5] Storing Enterprise Credentials with zero-plaintext Git exposure..."
vault kv put secret/production/app-config \
  DB_HOST="postgres-primary.db-tier.svc.cluster.local" \
  DB_PORT="5432" \
  DB_NAME="enterprise_prod" \
  DB_USER="app_vault_svc" \
  DB_PASSWORD="vLt_$(openssl rand -hex 16)" \
  PAYMENT_GATEWAY_API_KEY="sk_live_$(openssl rand -hex 24)" \
  JWT_SIGNING_SECRET="$(openssl rand -base64 32)"

echo "[✓] Credentials stored securely with versioned key-value metadata."

echo "[3/5] Applying Least-Privilege Vault Access Policy..."
vault policy write enterprise-app-prod-policy secret_management/vault-policy.hcl

echo "[4/5] Enabling & Configuring Kubernetes Authentication Backend..."
vault auth enable kubernetes || echo "Kubernetes auth already enabled."

vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc:443"

vault write auth/kubernetes/role/enterprise-app-role \
  bound_service_account_names=enterprise-app-sa \
  bound_service_account_namespaces=production \
  policies=enterprise-app-prod-policy \
  ttl=1h \
  max_ttl=24h

echo "[✓] Vault Kubernetes Auth Role bound to ServiceAccount 'enterprise-app-sa'."

echo "[5/5] Deploying External Secrets Operator Custom Resources..."
kubectl apply -f secret_management/secret-store.yaml
kubectl apply -f secret_management/external-secret.yaml

echo "================================================================="
echo " [✓] VAULT PIPELINE INTEGRATION READY & SECURE"
echo " Secret handling compliance: Zero Plaintext in Git (CSI / ESO Synced)"
echo "================================================================="
