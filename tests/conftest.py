"""Setup tests."""
# pylint: disable=redefined-outer-name,unused-argument
import os
import time
import uuid
from typing import Callable, Generator

import pytest

from http_server_mock import HttpServerMock, _RunInBackground
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_sqs.service_resource import Queue
from utils import create_queue, create_table

from inference_engine.consumer.consumer import ComputeResultCallableT, Consumer
from inference_engine.dynamo_db_client import DynamoDBClient
from inference_engine.producer.producer import Producer


@pytest.fixture
def sqs_queue_name() -> str:
    return f"queue_{uuid.uuid4()}.fifo"


@pytest.fixture
def sqs_endpoint_url() -> str:
    return os.environ.get("SQS_ENDPOINT_URL", "http://localhost:9324")


@pytest.fixture
def ddb_table_name() -> str:
    return f"table_{uuid.uuid4()}"


@pytest.fixture
def ddb_endpoint_url() -> str:
    return os.environ.get("DDB_ENDPOINT_URL", "http://localhost:8000")


@pytest.fixture
def boto3_ddb_resource_kwargs(ddb_endpoint_url: str) -> dict:
    return {
        "use_ssl": False,
        "endpoint_url": ddb_endpoint_url,
        "aws_secret_access_key": "x",
        "aws_access_key_id": "x",
        "region_name": "local",
    }


@pytest.fixture
def ddb_table(
    ddb_table_name: str, boto3_ddb_resource_kwargs: dict
) -> Generator[Table, None, None]:
    table = create_table(ddb_table_name, **boto3_ddb_resource_kwargs)
    yield table
    table.delete()


@pytest.fixture
def ddb_client(
    ddb_table_name: str,
    boto3_ddb_resource_kwargs: dict,
    ddb_table: Table,
) -> DynamoDBClient:
    return DynamoDBClient(
        table_name=ddb_table_name, **boto3_ddb_resource_kwargs
    )


@pytest.fixture
def _create_queue(
    boto3_sqs_resource_kwargs: dict,
    sqs_queue_name: str,
) -> Generator[tuple[Queue, Queue], None, None]:
    queue, dl_queue = create_queue(sqs_queue_name, **boto3_sqs_resource_kwargs)
    yield queue, dl_queue
    queue.purge()
    queue.delete()
    dl_queue.purge()
    dl_queue.delete()


@pytest.fixture
def sqs_queue(
    _create_queue: tuple[Queue, Queue],
) -> Queue:
    queue, _ = _create_queue
    return queue


@pytest.fixture
def dl_queue(_create_queue: tuple[Queue, Queue]) -> Queue:
    _, dlq = _create_queue
    return dlq


@pytest.fixture
def boto3_sqs_resource_kwargs(sqs_endpoint_url: str) -> dict:
    return {
        "region_name": "elasticmq",
        "aws_secret_access_key": "x",
        "aws_access_key_id": "x",
        "use_ssl": False,
        "endpoint_url": sqs_endpoint_url,
    }


@pytest.fixture
def producer(
    sqs_queue_name: str,
    sqs_queue: Queue,
    ddb_client: DynamoDBClient,
    boto3_sqs_resource_kwargs: dict,
) -> Generator[Producer, None, None]:
    yield Producer(
        queue_name=sqs_queue_name,
        ddb_client=ddb_client,
        **boto3_sqs_resource_kwargs,
        poll_time_seconds=0.1,
        timeout_seconds=1,
    )


@pytest.fixture
def compute_result_function() -> ComputeResultCallableT:
    def function(body, message_id):
        return {"received_body": body, "message_id": message_id}

    return function


@pytest.fixture
def consumer(
    compute_result_function: Callable,
    boto3_sqs_resource_kwargs: dict,
    ddb_client: DynamoDBClient,
    sqs_queue_name: str,
    sqs_queue: Queue,
    mock_ecs_agent_task_protection_server: HttpServerMock,
) -> Generator[Consumer, None, None]:
    _consumer = Consumer(
        sqs_queue_name,
        ddb_client=ddb_client,
        compute_result=compute_result_function,
        enable_ecs_scalein_protection=True,
        **boto3_sqs_resource_kwargs,
    )
    _consumer.start_consuming()
    time.sleep(0.1)
    yield _consumer
    _consumer.stop_consuming()


@pytest.fixture
def request_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def mock_ecs_agent_task_protection_server() -> (
    Generator[_RunInBackground, None, None]
):
    app = HttpServerMock(__name__)

    @app.route("/task-protection/v1/state", methods=["GET", "PUT"])
    def state():
        return {
            "protection": {
                "ExpirationDate": "2022-10-06T02:29:16Z",
                "ProtectionEnabled": True,
                "TaskArn": "arn:aws:ecs:us-west-2:111122223333:task/1234567890abcdef0",  # noqa: E501
            }
        }

    port = 5000
    host = "localhost"
    ecs_agent_uri = f"http://{host}:{port}"
    os.environ["ECS_AGENT_URI"] = ecs_agent_uri
    run_in_background = app.run(host, port)

    with run_in_background:
        yield run_in_background

    os.environ.pop("ECS_AGENT_URI")
