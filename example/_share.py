import json
import os
from typing import Any

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_sqs.service_resource import Queue, SQSServiceResource

from inference_engine.dynamo_db_client import DynamoDBClient


def ddb_table_name() -> str:
    return os.environ.get("DDB_TABLE_NAME", "example_table")


def sqs_queue_name() -> str:
    return os.environ.get("SQS_QUEUE_NAME", "example_queue.fifo")


def ddb_kwargs() -> dict[str, Any]:
    if use_ssl := os.environ.get("DDB_USE_SSL"):
        use_ssl = use_ssl.lower() != "false"

    kwargs = {
        "aws_access_key_id": os.environ.get("DDB_AWS_ACCESS_KEY_ID"),
        "endpoint_url": os.environ.get("DDB_ENDPOINT_URL"),
        "aws_secret_access_key": os.environ.get("DDB_AWS_SECRET_ACCESS_KEY"),
        "region_name": os.environ.get("DDB_REGION_NAME"),
        "use_ssl": use_ssl,
    }
    return {k: v for k, v in kwargs.items() if v is not None}


def ddb_client() -> DynamoDBClient:
    return DynamoDBClient(
        table_name=ddb_table_name(),
        **ddb_kwargs(),
    )


def create_table(
    tolerate_already_exists: bool = True,
) -> Table:
    table_name = ddb_table_name()
    kwargs = ddb_kwargs()
    dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb", **kwargs)
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "message_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "message_id", "AttributeType": "S"},
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        if not tolerate_already_exists:
            raise
        table = dynamodb.Table(table_name)

    dynamodb.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    return table


def sqs_kwargs() -> dict[str, Any]:
    if use_ssl := os.environ.get("SQS_USE_SSL"):
        use_ssl = use_ssl.lower() != "false"

    kwargs = {
        "region_name": os.environ.get("SQS_REGION_NAME"),
        "aws_secret_access_key": os.environ.get("SQS_AWS_SECRET_ACCESS_KEY"),
        "aws_access_key_id": os.environ.get("SQS_AWS_ACCESS_KEY_ID"),
        "endpoint_url": os.environ.get("SQS_ENDPOINT_URL"),
        "use_ssl": use_ssl,
    }
    return {k: v for k, v in kwargs.items() if v}


def create_queue() -> Queue:
    kwargs = sqs_kwargs()
    queue_name = sqs_queue_name()
    sqs: SQSServiceResource = boto3.resource("sqs", **kwargs)

    dl_queue = sqs.create_queue(
        QueueName=f"dl_{queue_name}",
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true",
            "VisibilityTimeout": "2",
            "MessageRetentionPeriod": "86400",
        },
    )

    dl_arn = dl_queue.url.split("/")[-2:]
    dl_arn = f"arn:aws:sqs:elasticmq:{':'.join(dl_arn)}"

    queue = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true",
            "VisibilityTimeout": "1",
            "MessageRetentionPeriod": "86400",
            "RedrivePolicy": json.dumps(
                {"deadLetterTargetArn": dl_arn, "maxReceiveCount": "5"}
            ),
        },
    )
    return queue
