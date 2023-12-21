"""Heartbeat thread for SQS Consumer."""
from __future__ import annotations

import threading
from typing import Optional

import boto3
from loguru import logger
from mypy_boto3_sqs.client import SQSClient

from ..exceptions import HeartbeatStopTimeoutError


class Heartbeat:
    """Heartbeat thread for SQS Consumer.

    This class defines a "Heartbeat" for a SQS message receive.
    The mechanism is described in:
    https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html  # noqa: E501

    The idea is that this class can be used to start a background thread that
    should last for the duration of the calling thread processing the message.
    This thread sends a "heartbeat" to SQS, telling SQS that the message
    is still being processed.

    This is impmented by using the ChangeMessageVisibility call for the
    receipt_handle. This class will make the ChangeMessageVisibility every
    <interval> seconds, where it will futher increase the visibility timeout
    by <visibility_timeout> seconds.

    In SQS, the visibility timeout sets the timeout before the SQS message
    can be picked by other consumers.

    """

    def __init__(
        self,
        *,
        queue_url: str,
        receipt_handle: str,
        message_id: str,
        visibility_timeout: int = 30,
        interval: float = 10,
        start_immediately: bool = False,
        default_stop_timeout: Optional[float] = 5,
        join_on_stop: bool = False,
        **boto3_sqs_resource_kwargs,
    ):
        """Get a new Heartbeat.

        Parameters
        ----------
        queue_url : str
            The URL for the SQS queue.
        receipt_handle : str
            Receipt handle for message receive.
        message_id : str
            Message ID (only used for logging).
        visibility_timeout : int
            The visibility timeout that should be set for the receipt_id.
        interval : float
            The interval with which to send a heartbeat.
            In order to have robustness, this should be set such that
            interval ~= visibility_timeout / 3
        start_immediately : bool
            Whether to start the background thread immediatly upon __init__.
        default_stop_timeout : float
          The default timeout to use on Thread.join.
        join_on_stop : bool
            Whether to call join.

        """
        self._thread = threading.Thread(
            target=self._run, name=f"Heartbeat:{receipt_handle}"
        )
        self._stop_event = threading.Event()
        self.sqs_cli: SQSClient = boto3.client(
            "sqs", **boto3_sqs_resource_kwargs
        )
        self.queue_url = queue_url
        self.message_id = message_id
        self.receipt_handle = receipt_handle

        if interval + 1 > visibility_timeout:
            raise ValueError(
                "Interval should be atleast 1 second < visibility_timeout"
            )

        self.visibility_timeout = visibility_timeout
        self.interval = interval
        self.default_stop_timeout = default_stop_timeout
        self.join_on_stop = join_on_stop
        self.logger = logger.bind(
            queue_url=self.queue_url,
            message_id=self.message_id,
            receipt_handle=self.receipt_handle,
            thread_ident=self._thread.ident,
            visibility_timeout=self.visibility_timeout,
            interval=self.interval,
        )
        if start_immediately:
            self.start()

    @property
    def is_running(self) -> bool:
        """Check if heartbeat thread is alive."""
        return self._thread.is_alive()

    def start(self) -> Heartbeat:
        """Start the Heartbeat thread."""
        if not self.is_running:
            self._thread.start()
            self.logger.info("Started heartbeat thread")

        return self

    def stop(self, timeout: Optional[float] = None) -> None:
        """Stop the heartbeat thread.

        Parameters
        ----------
        timeout : float, optional
            The timeout to use. If None then the default_stop_timeout is used.

        Raises
        ------
        HeartbeatStopTimeoutError
            If the Thread fails to join within the timeout.

        """
        timeout = timeout or self.default_stop_timeout
        self._stop_event.set()  # type: ignore
        if self.is_running and self.join_on_stop:
            self._thread.join(timeout=timeout)

            if self.is_running:
                raise HeartbeatStopTimeoutError(
                    f"Heartbeat thread join hit timeout "
                    f"after {timeout} seconds, "
                    f"thread_ident={self._thread.ident}"
                )

        self._stop_event.clear()

    def _run(self):
        num_fails = 0
        wait_time = self.interval
        while not self._stop_event.wait(wait_time):
            try:
                self.send_heartbeat()
            except Exception as exp:
                num_fails += 1
                self.logger.opt(exception=True).error(
                    "Failed to set heartbeat {}, num_fails={}",
                    str(exp),
                    num_fails,
                )
                # Don't wait full interval so that we can retry quickly
                wait_time = 0.1
            else:
                self.logger.debug("Successfully sent heartbeat to SQS.")
                wait_time = self.interval

        self.logger.info("Heartbeat thread received stop event")
        try:
            self.sqs_cli.close()
        except Exception as exp:
            self.logger.opt(exception=True).error(
                "Exp closing SQS cli connection: {}", str(exp)
            )

    def send_heartbeat(self) -> bool:
        """Send heartbeat.

        Returns
        -------
        bool
            Whether the change_message_visibility call succeeded.

        """
        response = self.sqs_cli.change_message_visibility(
            QueueUrl=self.queue_url,
            ReceiptHandle=self.receipt_handle,
            VisibilityTimeout=self.visibility_timeout,
        )

        return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def __enter__(self):
        """Enter the context and start the heartbeat."""
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and stop the heartbeat."""
        self.stop()
