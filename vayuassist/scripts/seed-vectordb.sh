#!/usr/bin/env bash
set -euo pipefail

# Seed Pinecone vector index with monsoon protocol documents.

REGION="${AWS_REGION:-us-east-1}"
SEED_SCRIPT="${SEED_SCRIPT:-../backend/src/data/seed_rag.py}"

if [[ -z "${PINECONE_API_KEY:-}" ]]; then
  echo "Fetching Pinecone API key from Secrets Manager..."
  SECRET=$(aws secretsmanager get-secret-value \
    --secret-id vayuassist/api_keys \
    --region "$REGION" \
    --query SecretString \
    --output text)
  export PINECONE_API_KEY
  PINECONE_API_KEY=$(echo "$SECRET" | python -c "import sys,json; print(json.load(sys.stdin)['pinecone_api_key'])")
  export PINECONE_API_KEY
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  SECRET=$(aws secretsmanager get-secret-value \
    --secret-id vayuassist/api_keys \
    --region "$REGION" \
    --query SecretString \
    --output text)
  export OPENAI_API_KEY
  OPENAI_API_KEY=$(echo "$SECRET" | python -c "import sys,json; print(json.load(sys.stdin)['openai_api_key'])")
  export OPENAI_API_KEY
fi

echo "Running seed script: $SEED_SCRIPT"
cd "$(dirname "$SEED_SCRIPT")/.."
python -m src.data.seed_rag

echo "Vector DB seeded."
