"""Tests for the Consumer."""
# pylint: disable=redefined-outer-name,unused-argument
import time

import pytest

from inference_engine.consumer import Consumer, ConsumerAlreadyConsumingError
from inference_engine.dynamo_db_client import DynamoDBClient


def _only_kws_callable(*, x, y, z):
    pass


def _not_enough_args_callable():
    pass


def test_running(consumer: Consumer):
    assert consumer.is_running


def test_ping(consumer: Consumer):
    consumer.ping_queue()


@pytest.mark.parametrize(
    "bad_callable", [_not_enough_args_callable, _only_kws_callable]
)
def test_bad_callable_only_kw(
    ddb_client: DynamoDBClient,
    bad_callable,
    boto3_sqs_resource_kwargs: dict,
):
    with pytest.raises(ValueError):
        _ = Consumer(
            queue_name="foo",
            ddb_client=ddb_client,
            compute_result=bad_callable,
            **boto3_sqs_resource_kwargs,
        )


def test_already_running(consumer: Consumer):
    assert consumer.is_running
    with pytest.raises(ConsumerAlreadyConsumingError):
        consumer.start_consuming()


def test_stop(consumer: Consumer):
    assert consumer.is_running
    consumer.stop_consuming()
    assert not consumer.is_running


def test_restart(consumer: Consumer):
    assert consumer.is_running
    consumer.stop_consuming()
    consumer.start_consuming()
    time.sleep(0.1)
    assert consumer.is_running


def test_multiple_stop_ok(consumer: Consumer):
    assert consumer.is_running
    consumer.stop_consuming()
    consumer.stop_consuming()
    assert not consumer.is_running


def test_is_processing_no_messages(consumer: Consumer):
    assert not consumer.is_processing_message
