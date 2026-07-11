resource "aws_secretsmanager_secret" "api_keys" {
  name = "vayuassist/api_keys"
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    openai_api_key    = "REPLACE_ME"
    gemini_api_key    = "REPLACE_ME"
    pinecone_api_key  = "REPLACE_ME"
    twilio_account_sid = "REPLACE_ME"
    twilio_auth_token  = "REPLACE_ME"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret" "jwt" {
  name = "vayuassist/jwt"
}

resource "aws_secretsmanager_secret" "encryption" {
  name = "vayuassist/encryption"
}
