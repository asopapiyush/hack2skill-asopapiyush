"""Application settings: env vars locally, Secrets Manager on AWS."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .aws import get_secret_value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    aws_region: str = "us-east-1"

    database_url: str = "postgresql://vayuassist:vayuassist@localhost:5432/vayuassist"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me"
    openai_api_key: str = ""
    pinecone_api_key: str = ""

    sqs_notifications_url: str = ""
    sqs_sms_outbound_url: str = ""
    sns_alerts_arn: str = ""

    def load_aws_secrets(self) -> None:
        """Overlay settings from Secrets Manager when running on AWS."""
        if self.env in ("development", "local", "test"):
            return

        self.database_url = get_secret_value(
            "vayuassist/database", "database_url", self.database_url
        )
        self.redis_url = get_secret_value(
            "vayuassist/redis", "url", self.redis_url
        )
        self.jwt_secret_key = get_secret_value(
            "vayuassist/jwt", "secret_key", self.jwt_secret_key
        )
        self.openai_api_key = get_secret_value(
            "vayuassist/api_keys", "openai_api_key", self.openai_api_key
        )
        self.pinecone_api_key = get_secret_value(
            "vayuassist/api_keys", "pinecone_api_key", self.pinecone_api_key
        )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.load_aws_secrets()
    return settings
