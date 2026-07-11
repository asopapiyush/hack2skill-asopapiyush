"""AWS service clients and Secrets Manager helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
USE_AWS = os.getenv("ENV", "development") not in ("development", "local", "test")


@lru_cache
def _session() -> boto3.Session:
    return boto3.Session(region_name=AWS_REGION)


def secrets_client():
    return _session().client("secretsmanager")


def sqs_client():
    return _session().client("sqs")


def sns_client():
    return _session().client("sns")


def s3_client():
    return _session().client("s3")


def cloudwatch_client():
    return _session().client("cloudwatch")


def get_secret(secret_id: str) -> dict[str, Any]:
    """Fetch and parse a JSON secret from Secrets Manager."""
    if not USE_AWS:
        return {}

    response = secrets_client().get_secret_value(SecretId=secret_id)
    return json.loads(response["SecretString"])


def get_secret_value(secret_id: str, key: str, default: str = "") -> str:
    """Get a single key from a JSON secret, with env var fallback."""
    env_key = key.upper()
    if os.getenv(env_key):
        return os.environ[env_key]

    if not USE_AWS:
        return default

    secret = get_secret(secret_id)
    return str(secret.get(key, default))


def put_metric(
    namespace: str,
    name: str,
    value: float,
    unit: str = "Count",
    dimensions: dict[str, str] | None = None,
) -> None:
    """Publish a custom CloudWatch metric."""
    if not USE_AWS:
        return

    metric: dict[str, Any] = {
        "MetricName": name,
        "Value": value,
        "Unit": unit,
    }
    if dimensions:
        metric["Dimensions"] = [
            {"Name": k, "Value": v} for k, v in dimensions.items()
        ]

    cloudwatch_client().put_metric_data(
        Namespace=namespace,
        MetricData=[metric],
    )


def send_sqs_message(queue_url: str, body: str) -> None:
    sqs_client().send_message(QueueUrl=queue_url, MessageBody=body)


def publish_sns(topic_arn: str, message: str, subject: str = "VayuAssist") -> None:
    sns_client().publish(TopicArn=topic_arn, Message=message, Subject=subject)
