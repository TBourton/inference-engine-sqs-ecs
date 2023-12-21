"""Shared SQS functionality."""
import json
from typing import Literal

import boto3
from mypy_boto3_sqs.service_resource import Message, Queue, SQSServiceResource

from .dynamo_db_client import DynamoDBClient
from .exceptions import SQSConnectionError
from .types import JsonStrT, JsonT, MessageAsDictT


class _SQSBase:
    def __init__(
        self,
        queue_name: str,
        *,
        ddb_client: DynamoDBClient,
        **boto3_sqs_resource_kwargs,
    ):
        self.queue_name = queue_name
        self.ddb_client = ddb_client
        self._boto3_sqs_resource_kwargs = boto3_sqs_resource_kwargs
        self.sqs: SQSServiceResource = boto3.resource(
            "sqs", **boto3_sqs_resource_kwargs
        )
        self.queue: Queue = self.sqs.get_queue_by_name(
            QueueName=self.queue_name
        )

    def ping_queue(self) -> Literal["pong"]:
        """Test queue connection.

        Returns
        -------
        str

        Raises
        ------
        SQSConnectionError
            If queue cannot be reached.

        """
        try:
            _ = self.sqs.meta.client.get_queue_url(QueueName=self.queue_name)
        except Exception as exp:
            raise SQSConnectionError(str(exp)) from exp

        return "pong"


def serialise_message_body(body: JsonT) -> JsonStrT:
    """Serialise the message body.

    Parameters
    ----------
    body : obj
        Any json.dumps addmissable object.

    Returns
    -------
    str
        The serialised message body.

    """
    return json.dumps(body)


def deserialise_message_body(json_str: JsonStrT) -> JsonT:
    """Deserialise the message body.

    Parameters
    ----------
    json_str : str
        The serialised message body.

    Returns
    -------
    obj
        The message body.

    """
    return json.loads(json_str)


def message_to_dict(message: Message) -> MessageAsDictT:
    """Serialise a message to dict (for writing to DB purposes)."""
    return {
        "body": message.body,
        "attributes": message.attributes,
        "md5_of_body": message.md5_of_body,
        "md5_of_message_attributes": message.md5_of_message_attributes,
        "message_attributes": message.message_attributes,
        "message_id": message.message_id,
    }
