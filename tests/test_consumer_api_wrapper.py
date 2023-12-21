"""Test Consumer API wrapper."""
# pylint: disable=redefined-outer-name,unused-argument

from typing import Generator

import pytest
from pytest_mock import MockerFixture

from fastapi import FastAPI
from fastapi.testclient import TestClient

from inference_engine.consumer.api_wrapper import get_app
from inference_engine.consumer.consumer import Consumer


@pytest.fixture
def app(consumer: Consumer) -> Generator[FastAPI, None, None]:
    yield get_app(consumer)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_:
        yield client_


@pytest.mark.parametrize("route", ["busy", "ready", "health"])
def test_happy(client: TestClient, route: str):
    assert client.get(f"/{route}").status_code == 200


def test_busy(client: TestClient, mocker: MockerFixture, consumer: Consumer):
    _ = mocker.patch(
        "inference_engine.consumer.consumer.Consumer.is_processing_message",
        return_value=True,
    )
    assert client.get("/busy").status_code == 503


def test_ready(client: TestClient, mocker: MockerFixture, consumer: Consumer):
    _ = mocker.patch.object(consumer, "ping_queue", side_effect=RuntimeError)
    assert client.get("/ready").status_code == 500


@pytest.mark.parametrize("route", ["ready", "health"])
def test_shutdown(client: TestClient, consumer: Consumer, route: str):
    consumer.stop_consuming()
    assert not consumer.is_running
    assert client.get(f"/{route}").status_code == 500
