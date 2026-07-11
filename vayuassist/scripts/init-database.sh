#!/usr/bin/env bash
set -euo pipefail

# Run database schema/migrations against RDS.
# Requires: psql or alembic, DATABASE_URL in env or Secrets Manager.

REGION="${AWS_REGION:-us-east-1}"
SCHEMA_FILE="${SCHEMA_FILE:-../backend/src/database/schema.sql}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Fetching DATABASE_URL from Secrets Manager..."
  SECRET=$(aws secretsmanager get-secret-value \
    --secret-id vayuassist/database \
    --region "$REGION" \
    --query SecretString \
    --output text)
  DATABASE_URL=$(echo "$SECRET" | python -c "import sys,json; print(json.load(sys.stdin)['database_url'])")
  export DATABASE_URL
fi

echo "Applying schema from $SCHEMA_FILE..."
if command -v psql &>/dev/null; then
  psql "$DATABASE_URL" -f "$SCHEMA_FILE"
elif [[ -d "../backend/alembic" ]]; then
  cd ../backend && alembic upgrade head
else
  echo "No psql or alembic found. Install psql or set up Alembic migrations."
  exit 1
fi

echo "Database initialized."
