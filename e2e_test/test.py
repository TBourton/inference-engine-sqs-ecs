"""E2E test."""
# pylint: disable=redefined-outer-name,unused-argument
import uuid
from typing import Any

import pytest

from inference_engine.producer.producer import Producer
from inference_engine.types import ResultStatus


def test_ping_queue(producer: Producer):
    producer.ping_queue()


@pytest.fixture
def request_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def message_body() -> dict[str, Any]:
    # This might change depending on example
    return {
        "parameters": [1, 2, 3, "a", "b", "c"],
        "FUNCTION_PROC_TIME": 1,
    }


def test_send_message(
    producer: Producer, message_body: dict[str, Any], request_id: str
):
    resp = producer.post(message_body, request_id=request_id)
    print(resp)
    assert resp.status == ResultStatus.SUCCESS
    assert resp.status_code == 200
    assert not resp.error
    assert resp.request_id == request_id
