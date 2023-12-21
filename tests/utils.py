"""Utils for testing."""
import json

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_sqs.service_resource import Queue, SQSServiceResource


def create_table(
    table_name: str,
    tolerate_already_exists: bool = False,
    **kwargs,
) -> Table:
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


def create_queue(queue_name: str, **kwargs) -> tuple[Queue, Queue]:
    sqs: SQSServiceResource = boto3.resource("sqs", **kwargs)

    dl_queue = sqs.create_queue(
        QueueName=f"dl_{queue_name}",
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true",
            "VisibilityTimeout": "1",
            "MessageRetentionPeriod": "600",
        },
    )

    dl_arn = dl_queue.url.split("/")[-2:]
    dl_arn = f"arn:aws:sqs:elasticmq:{':'.join(dl_arn)}"

    queue = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true",
            "VisibilityTimeout": "0",
            "MessageRetentionPeriod": "300",
            "RedrivePolicy": json.dumps(
                {"deadLetterTargetArn": dl_arn, "maxReceiveCount": "5"}
            ),
        },
    )
    return queue, dl_queue
