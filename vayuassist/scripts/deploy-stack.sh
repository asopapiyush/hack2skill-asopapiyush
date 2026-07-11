#!/usr/bin/env bash
set -euo pipefail

# Deploy or update the full AWS stack via Terraform.

ENVIRONMENT="${1:-dev}"
TFVARS="environments/${ENVIRONMENT}.tfvars"
INFRA_DIR="$(cd "$(dirname "$0")/../infrastructure" && pwd)"

if [[ ! -f "$INFRA_DIR/$TFVARS" ]]; then
  echo "Usage: $0 [dev|prod]"
  exit 1
fi

cd "$INFRA_DIR"

echo "==> Initializing Terraform..."
terraform init

echo "==> Planning ($ENVIRONMENT)..."
terraform plan -var-file="$TFVARS" -out="tfplan-${ENVIRONMENT}"

read -r -p "Apply plan for $ENVIRONMENT? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

terraform apply "tfplan-${ENVIRONMENT}"
terraform output

echo "Stack deployed. Next: ./scripts/create-secrets.sh && ./scripts/init-database.sh"
