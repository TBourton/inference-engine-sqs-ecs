"""Tests for the Consumer."""
from inference_engine.producer import Producer


def test_ping(producer: Producer):
    producer.ping_queue()
