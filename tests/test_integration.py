"""Test the overall system integration."""
import time

import pytest

from http_server_mock import _RunInBackground
from mypy_boto3_sqs.service_resource import Queue

import inference_engine
from inference_engine.consumer.consumer import Consumer
from inference_engine.exceptions import (
    AwaitingResultTimeoutError,
    ResultErrorStatusError,
)
from inference_engine.producer.producer import Producer
from inference_engine.types import ResultStatus


def test_version():
    assert inference_engine.__version__


def test_happy(consumer: Consumer, producer: Producer, request_id: str):
    body = {"parameters": [1, 2, 3]}
    resp = producer.post(body, request_id=request_id)
    assert resp.status == ResultStatus.SUCCESS
    assert resp.status_code == 200
    assert resp.request_id == request_id
    assert not resp.error
    assert resp.result == consumer.compute_result(body, resp.message_id)


def test_happy_non_blocking(
    consumer: Consumer, producer: Producer, request_id: str
):
    body = {"parameters": [1, 2, 3]}
    id_ = producer.post_non_blocking(body, request_id=request_id)

    timeout = time.time() + 5
    poll_time = 0.1
    while time.time() < timeout:
        status = producer.retrieve_result_status(id_)
        assert status in [
            ResultStatus.IN_PROGRESS,
            ResultStatus.SUCCESS,
            ResultStatus.SUBMITTED,
        ]
        if status == ResultStatus.SUCCESS:
            break
        time.sleep(poll_time)
    else:
        raise TimeoutError

    resp = producer.retrieve_result(id_)
    assert resp.message_id == id_
    assert resp.status == ResultStatus.SUCCESS
    assert resp.request_id == request_id
    assert resp.status_code == 200
    assert not resp.error
    assert resp.result == consumer.compute_result(body, resp.message_id)


def test_retryable_exp_in_compute_function(
    consumer: Consumer, producer: Producer
):
    def raise_exp(_, message_id):
        raise RuntimeError(message_id)

    consumer.compute_result = raise_exp

    body = {"parameters": [1, 2, 3]}
    resp = producer.post(body)
    assert resp.status_code == 500
    assert isinstance(resp.error, AwaitingResultTimeoutError)
    assert consumer.is_running
    assert not resp.result


def test_timeout(consumer: Consumer, producer: Producer):
    def wait(_, __):
        time.sleep(1)

    consumer.compute_result = wait

    body = {"parameters": [1, 2, 3]}
    producer.timeout_seconds = 0.1
    resp = producer.post(body)
    assert resp.status_code == 500
    assert isinstance(resp.error, AwaitingResultTimeoutError)
    assert consumer.is_running
    assert not resp.result


def test_non_retryable_exp_in_compute_function(
    consumer: Consumer, producer: Producer
):
    class CustomExp(Exception):
        pass

    exp_msg = "Something went wrong abc123"
    exp = CustomExp(exp_msg)

    def raise_exp(_, message_id):
        raise exp

    consumer.compute_result = raise_exp
    consumer.non_retryable_errors = (CustomExp,)

    body = {"parameters": [1, 2, 3]}
    resp = producer.post(body)
    assert resp.status_code == 500
    assert isinstance(resp.error, ResultErrorStatusError)
    assert exp_msg in resp.error.args[0]
    assert not resp.result
    assert consumer.is_running


def test_ecs_agent_connection_broken_from_start(
    consumer: Consumer,
    producer: Producer,
    mock_ecs_agent_task_protection_server: _RunInBackground,
):
    """Test when ECS agent can't be reached from start of call."""
    mock_ecs_agent_task_protection_server.process.join(timeout=1)
    body = {"parameters": [1, 2, 3]}
    producer.timeout_seconds = 0.1
    resp = producer.post(body)
    assert resp.status_code == 500
    assert isinstance(resp.error, AwaitingResultTimeoutError)
    assert not resp.result
    assert consumer.is_running


@pytest.mark.usefixtures("consumer")
def test_message_is_deleted(
    producer: Producer, sqs_queue: Queue, dl_queue: Queue
):
    resp = producer.post({})
    assert resp.status == ResultStatus.SUCCESS
    assert resp.status_code == 200
    sqs_queue.load()
    assert not int(sqs_queue.attributes["ApproximateNumberOfMessages"])
    dl_queue.load()
    assert not int(dl_queue.attributes["ApproximateNumberOfMessages"])
