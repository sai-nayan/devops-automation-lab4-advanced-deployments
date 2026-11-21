# HashiCorp Vault Production Policy - Principle of Least Privilege
# Student: Sai Nayan Mamilla (sainayanmamilla)

# Allow read-only access to production microservice secrets
path "secret/data/production/*" {
  capabilities = ["read"]
}

# Allow reading metadata for version checking
path "secret/metadata/production/*" {
  capabilities = ["read", "list"]
}

# Explicitly deny write, update, or delete in production path
path "secret/data/production/*" {
  capabilities = ["read"]
}

# Deny root and system reconfiguration
path "sys/*" {
  capabilities = ["deny"]
}
