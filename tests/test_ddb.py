# pylint: disable=redefined-outer-name,unused-argument
import time
import uuid

import pytest
from pytest_lazyfixture import lazy_fixture

from inference_engine.dynamo_db_client import (
    AwaitingResultTimeoutError,
    DynamoDBClient,
    DynamoDBItem,
    ExpiredItemError,
    KeyNotFoundError,
    ResultErrorStatusError,
)
from inference_engine.types import ResultStatus


@pytest.fixture
def message_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def result():
    return {"meaning": 42}


@pytest.fixture
def in_progress_ttl() -> int:
    return 1


@pytest.fixture
def exp() -> Exception:
    return RuntimeError("Something went wrong during compute")


def test_item_success(message_id: str, result):
    assert DynamoDBItem(
        message_id=message_id, status=ResultStatus.SUCCESS, result=result
    )


def test_item_error(message_id: str, exp: Exception):
    assert DynamoDBItem(
        message_id=message_id,
        status=ResultStatus.ERROR,
        result=None,
        error=str(exp),
    )


@pytest.fixture
def result_put(
    message_id: str,
    ddb_client: DynamoDBClient,
    result,
) -> None:
    ddb_client.result_put(message_id=message_id, result=result)


@pytest.fixture
def error_put(
    message_id: str,
    ddb_client: DynamoDBClient,
    exp: Exception,
) -> None:
    ddb_client.error_put(message_id=message_id, exp=exp)


@pytest.fixture
def in_progress_put(
    message_id: str, ddb_client: DynamoDBClient, in_progress_ttl: int
) -> None:
    ddb_client.in_progress_put(in_progress_ttl, message_id=message_id)


@pytest.fixture
def submitted_put(
    message_id: str, ddb_client: DynamoDBClient, in_progress_ttl: int
) -> None:
    ddb_client.submitted_put(in_progress_ttl, message_id=message_id)


def test_item_exists(
    result_put: None, ddb_client: DynamoDBClient, message_id: str
):
    assert ddb_client.item_exists(message_id)


def test_result_get(
    result_put: None, ddb_client: DynamoDBClient, message_id: str, result
):
    assert ddb_client.result_get(message_id) == result


def test_result_poll_success(
    result_put: None, ddb_client: DynamoDBClient, message_id: str, result
):
    assert ddb_client.result_poll(message_id) == result


def test_result_poll_timeout(
    ddb_client: DynamoDBClient, message_id: str, result
):
    with pytest.raises(AwaitingResultTimeoutError):
        _ = ddb_client.result_poll(message_id, timeout_seconds=0.1)


def test_result_get_doesnt_exist(
    ddb_client: DynamoDBClient, message_id: str, result
):
    with pytest.raises(KeyNotFoundError):
        _ = ddb_client.result_get(message_id)


def test_result_get_on_error(
    error_put: None,
    ddb_client: DynamoDBClient,
    message_id: str,
):
    with pytest.raises(ResultErrorStatusError):
        _ = ddb_client.result_get(message_id)


def test_error_get(
    ddb_client: DynamoDBClient,
    message_id: str,
    error_put: None,
):
    item = ddb_client.item_get(message_id)
    assert not item.result
    assert item.status == ResultStatus.ERROR
    assert item.message_id == message_id


def test_in_progress_get(
    ddb_client: DynamoDBClient,
    message_id: str,
    in_progress_put: None,
):
    item = ddb_client.item_get(message_id)
    assert not item.result
    assert item.status == ResultStatus.IN_PROGRESS
    assert item.message_id == message_id


def test_expired(
    ddb_client: DynamoDBClient,
    message_id: str,
    in_progress_put: None,
    in_progress_ttl: int,
):
    time.sleep(in_progress_ttl + 1)
    with pytest.raises(ExpiredItemError):
        _ = ddb_client.item_get(message_id)


def test_submitted_get(
    ddb_client: DynamoDBClient,
    message_id: str,
    submitted_put: None,
):
    item = ddb_client.item_get(message_id)
    assert not item.result
    assert item.status == ResultStatus.SUBMITTED
    assert item.message_id == message_id


@pytest.mark.parametrize(
    "_,status",
    [
        (lazy_fixture("result_put"), ResultStatus.SUCCESS),
        (lazy_fixture("error_put"), ResultStatus.ERROR),
        (lazy_fixture("in_progress_put"), ResultStatus.IN_PROGRESS),
        (lazy_fixture("submitted_put"), ResultStatus.SUBMITTED),
    ],
)
def test_status_get(
    ddb_client: DynamoDBClient, _: None, status: ResultStatus, message_id: str
):
    assert ddb_client.status_get(message_id) == status


@pytest.mark.parametrize(
    "_,expected",
    [
        (lazy_fixture("result_put"), True),
        (lazy_fixture("error_put"), False),
        (lazy_fixture("in_progress_put"), False),
        (lazy_fixture("submitted_put"), False),
        (None, False),
    ],
)
def test_result_exists(
    ddb_client: DynamoDBClient, _: None, expected: bool, message_id: str
):
    assert ddb_client.result_exists(message_id) is expected
