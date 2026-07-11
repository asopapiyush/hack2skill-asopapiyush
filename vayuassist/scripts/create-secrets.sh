#!/usr/bin/env bash
set -euo pipefail

# Populate Secrets Manager with API keys and JWT material.
# Run after: terraform apply (database/redis secrets are created by Terraform)

REGION="${AWS_REGION:-us-east-1}"
ENV_FILE="${1:-../.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Usage: $0 [path/to/.env]"
  echo "Create .env from .env.example first."
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

upsert_secret() {
  local name="$1"
  local payload="$2"
  if aws secretsmanager describe-secret --secret-id "$name" --region "$REGION" &>/dev/null; then
    aws secretsmanager put-secret-value \
      --secret-id "$name" \
      --secret-string "$payload" \
      --region "$REGION"
    echo "Updated secret: $name"
  else
    aws secretsmanager create-secret \
      --name "$name" \
      --secret-string "$payload" \
      --region "$REGION"
    echo "Created secret: $name"
  fi
}

upsert_secret "vayuassist/api_keys" "$(cat <<EOF
{
  "openai_api_key": "${OPENAI_API_KEY:-REPLACE_ME}",
  "gemini_api_key": "${GEMINI_API_KEY:-REPLACE_ME}",
  "pinecone_api_key": "${PINECONE_API_KEY:-REPLACE_ME}",
  "weather_api_key": "${WEATHER_API_KEY:-REPLACE_ME}",
  "speech_api_key": "${SPEECH_API_KEY:-REPLACE_ME}",
  "twilio_account_sid": "${TWILIO_ACCOUNT_SID:-REPLACE_ME}",
  "twilio_auth_token": "${TWILIO_AUTH_TOKEN:-REPLACE_ME}"
}
EOF
)"

upsert_secret "vayuassist/jwt" "$(cat <<EOF
{
  "secret_key": "${JWT_SECRET_KEY:-generate_a_secure_random_key_here}",
  "algorithm": "HS256",
  "expiry_seconds": 3600
}
EOF
)"

echo "Done. Database and Redis secrets are managed by Terraform."
