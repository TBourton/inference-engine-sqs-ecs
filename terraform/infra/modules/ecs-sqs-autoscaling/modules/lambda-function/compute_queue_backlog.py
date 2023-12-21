"""Determine queue backlog for an ECS service or task group.

This lambda function computes the following metrics.
    QueueBacklog - Non-negative integer that represents the estimated duration
        in seconds that a service or task group will take to process all items
        on a queue at the time of computation.
    QueueRequiresConsumer - Binary value (0 or 1), to be interpreted by the
        reader as a boolean, that indicates if a queue is backlogged with no
        consumer. If so, the value is '1'. Otherwise, the value is '0'.

"""

import datetime
import logging
import os
from typing import Any, Dict, Mapping

import boto3

log_level: str = os.environ.get("LOG_LEVEL", "INFO")
logger: logging.Logger = logging.getLogger("lambda.compute_queue_backlog")
logger.setLevel(log_level)

cw = boto3.client("cloudwatch")
ecs = boto3.client("ecs")
ssm = boto3.client("ssm")


def get_queue_metric_from_sqs(event: Mapping[str, Any]) -> int:
    """Retrieve the assigned queue metric for an SQS queue."""
    sqs = boto3.client("sqs")
    metric_name = event.get("metric_name", "ApproximateNumberOfMessages")
    queue_url = sqs.get_queue_url(
        QueueName=event["queue_name"],
        QueueOwnerAWSAccountId=event["queue_owner_aws_account_id"],
    )["QueueUrl"]
    queue_attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=[metric_name]
    )["Attributes"]

    return int(queue_attrs.get(metric_name, 0))


def lambda_handler(
    event: Mapping[str, Any], context: Mapping[str, Any]
) -> Dict[str, Any]:
    """Entrypoint to compute the metrics."""
    metric_value = get_queue_metric_from_sqs(event)

    cluster = event["cluster_name"]
    service = event["service_name"]
    queue_name = event["queue_name"]

    service_desc = ecs.describe_services(cluster=cluster, services=[service])[
        "services"
    ][0]
    num_tasks = service_desc["desiredCount"]

    queue_requires_consumer = 1 if num_tasks == 0 and metric_value > 0 else 0
    cw.put_metric_data(
        Namespace="AWS/ECS",
        MetricData=[
            {
                "MetricName": "QueueRequiresConsumer",
                "Dimensions": [
                    {"Name": "ClusterName", "Value": cluster},
                    {"Name": "ServiceName", "Value": service},
                    {"Name": "QueueName", "Value": queue_name},
                ],
                "Timestamp": datetime.datetime.utcnow(),
                "Value": queue_requires_consumer,
            }
        ],
    )
    logger.info(
        "Emitted QueueRequiresConsumer=%d for cluster=%s service=%s queue=%s.",
        queue_requires_consumer,
        cluster,
        service,
        queue_name,
        extra={
            "ctx": {
                "cluster_name": cluster,
                "service_name": service,
                "queue_name": queue_name,
                "queue_requires_consumer": queue_requires_consumer,
            }
        },
    )

    secs_per_msg = float(event.get("est_secs_per_msg", 1))

    if num_tasks > 0:
        backlog_secs = metric_value * secs_per_msg / num_tasks
    elif metric_value == 0:
        backlog_secs = 0
    else:
        # Backlog is undefined when there are no tasks but a message
        # backlog.
        return {}

    cw.put_metric_data(
        Namespace="AWS/ECS",
        MetricData=[
            {
                "MetricName": "QueueBacklog",
                "Dimensions": [
                    {"Name": "ClusterName", "Value": cluster},
                    {"Name": "ServiceName", "Value": service},
                    {"Name": "QueueName", "Value": queue_name},
                ],
                "Timestamp": datetime.datetime.utcnow(),
                "Value": backlog_secs,
            }
        ],
    )

    logger.info(
        "Emitted QueueBacklog=%d for cluster=%s service=%s queue=%s.",
        backlog_secs,
        cluster,
        service,
        queue_name,
        extra={
            "ctx": {
                "cluster_name": cluster,
                "service_name": service,
                "queue_name": queue_name,
                "queue_requires_consumer": queue_requires_consumer,
            }
        },
    )

    return {}
