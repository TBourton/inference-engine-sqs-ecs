"""Setup tests."""
# pylint: disable=redefined-outer-name,unused-argument
import os
from typing import Callable, Generator

import pytest

import boto3
from mypy_boto3_ssm.client import SSMClient

from inference_engine.dynamo_db_client import DynamoDBClient
from inference_engine.producer.producer import Producer


@pytest.fixture
def target_env() -> str:
    return os.environ.get("INFERENCE_ENGINE_TARGET_ENVIRONMENT", "staging")


@pytest.fixture
def ssm_producer_aws_access_key_id(target_env: str) -> str:
    return os.environ.get(
        "SSM_PRODUCER_AWS_ACCESS_KEY_ID",
        f"/inference/{target_env}/producer/aws_access_key_id",
    )


@pytest.fixture
def ssm_producer_aws_secret_access_key(target_env: str) -> str:
    return os.environ.get(
        "SSM_PRODUCER_AWS_SECRET_ACCESS_KEY",
        f"/inference/{target_env}/inference/producer/aws_secret_access_key",
    )


@pytest.fixture
def ssm_queue_name(target_env: str) -> str:
    return os.environ.get(
        "SSM_SQS_QUEUE_NAME", f"/inference/{target_env}/sqs/queue_name"
    )


@pytest.fixture
def ssm_table_name(target_env: str) -> str:
    return os.environ.get(
        "SSM_DDB_TABLE_NAME", f"/inference/{target_env}/dynamodb/table_name"
    )


@pytest.fixture
def ssm() -> Generator[SSMClient, None, None]:
    cli = boto3.client("ssm")
    yield cli
    cli.close()


@pytest.fixture
def get_parameter(ssm: SSMClient) -> Callable[[str, bool], str]:
    def inner(name: str, with_decryption: bool = False) -> str:
        resp = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
        return resp["Parameter"]["Value"]  # type: ignore

    return inner


@pytest.fixture
def aws_secret_access_key(
    get_parameter, ssm_producer_aws_secret_access_key: str
) -> str:
    return get_parameter(
        name=ssm_producer_aws_secret_access_key, with_decryption=True
    )


@pytest.fixture
def aws_access_key_id(
    get_parameter, ssm_producer_aws_access_key_id: str
) -> str:
    return get_parameter(ssm_producer_aws_access_key_id)


@pytest.fixture
def sqs_queue_name(get_parameter, ssm_queue_name: str) -> str:
    return get_parameter(ssm_queue_name)


@pytest.fixture
def ddb_table_name(get_parameter, ssm_table_name: str) -> str:
    return get_parameter(ssm_table_name)


@pytest.fixture
def aws_kwargs(
    aws_access_key_id: str, aws_secret_access_key: str
) -> dict[str, str]:
    return {
        "aws_secret_access_key": aws_secret_access_key,
        "aws_access_key_id": aws_access_key_id,
        "region_name": "eu-west-2",
    }


@pytest.fixture
def ddb_client(
    ddb_table_name: str, aws_kwargs: dict[str, str]
) -> DynamoDBClient:
    return DynamoDBClient(table_name=ddb_table_name, **aws_kwargs)


@pytest.fixture
def timeout() -> float:
    return float(os.environ.get("PRODUCER_TIMEOUT", 300))


@pytest.fixture
def producer(
    sqs_queue_name: str,
    ddb_client: DynamoDBClient,
    aws_kwargs: dict,
    timeout: float,
) -> Producer:
    return Producer(
        queue_name=sqs_queue_name,
        ddb_client=ddb_client,
        timeout_seconds=timeout,
        poll_time_seconds=timeout / 10,
        **aws_kwargs,
    )
