"""Consumer."""
import contextlib
import inspect
import threading
import time
import typing
from typing import Optional, Type

from loguru import logger
from mypy_boto3_sqs.service_resource import Message

from .._sqs_base import _SQSBase, deserialise_message_body
from .._sqs_base import message_to_dict as sqs_message_to_dict
from ..dynamo_db_client import DynamoDBClient
from ..exceptions import (
    ConsumerAlreadyConsumingError,
    ConsumerError,
    ConsumerRetryableError,
    ConsumerStopTimeoutError,
    ConsumerUnretryableError,
    ECSScaleInProtectionManagerError,
    HeartbeatStopTimeoutError,
)
from ..types import ComputeResultCallableT, ResultT
from ._ecs_scalein_protection_manager import ECSScaleInProtectionManager
from ._heartbeat import Heartbeat


class Consumer(_SQSBase):
    """Consumer.

    When it is running, this class:
    * Checks SQS for new messages
    * Processes the message
    * Stores the result in the DynamoDB table, using message_id as a key

    Example usage::

        def your_function(body, message_id):
            number = body["number"]
            # processing goes here
            return result

        consumer = Consumer(
            queue_name="sqs_queue_name.fifo",
            ddb_client=DynamoDBClient(table="ddb_table"),
            compute_result=your_function,
        )
        consumer.start_consuming()

    """

    def __init__(
        self,
        queue_name: str,
        *,
        queue_wait_time_seconds: int = 1,
        ddb_client: DynamoDBClient,
        compute_result: ComputeResultCallableT,
        in_progress_ttl_seconds: Optional[int] = 600,
        heartbeat_visibility_timeout: int = 30,
        heartbeat_interval: float = 10,
        enable_ecs_scalein_protection: bool = True,
        ecs_scalein_protection_manager_kwargs: Optional[
            dict[str, float | int | None | str]
        ] = None,
        non_retryable_errors: Optional[
            tuple[Type[Exception] | Exception, ...]
        ] = None,
        **boto3_sqs_resource_kwargs,
    ):
        """Get a new Consumer.

        Parameters
        ----------
        queue_name : str
            The name of the SQS queue to connect to.
        ddb_client : DynamoDBClient
            The pre-configured DynamoDBClient to use.
        queue_wait_time_seconds : int
            The SQS WaitTime parameter to use for SQS:RecieveMessage.
        compute_result: ComputeResultCallableT
            The callable used to compute the result.
        in_progress_ttl_seconds: int, optional
            The TTL to set on in_progress computations in DynamoDB.
        non_retryable_errors: tuple of Exception, optional
            Tuple of exceptions that should not be retried.
        heartbeat_visibility_timeout : int
            The visibility_timeout that should be set for heartbeat.
        heartbeat_interval: float
            The interval between sending heartbeats.
        enable_ecs_scalein_protection : bool
            Whether to attempt to call ECS agent scale in protection before
            attempting processing call.
        ecs_scalein_protection_manager_kwargs : dict, optional
            Dict of kwargs to pass onto the ECSScaleInProtectionManager
            __init__.
        kwargs: Any
            Kwargs passed onto the boto3 as boto3.resource("sqs", **kwargs).

        """
        _check_compute_result_callable(compute_result)

        super().__init__(
            queue_name=queue_name,
            ddb_client=ddb_client,
            **boto3_sqs_resource_kwargs,
        )

        self.non_retryable_errors: tuple[
            Exception | Type[Exception], ...
        ] = tuple(non_retryable_errors or [])
        self.queue_wait_time_seconds = queue_wait_time_seconds
        self.compute_result = compute_result
        self.heartbeat_visibility_timeout = heartbeat_visibility_timeout
        self.heartbeat_interval = heartbeat_interval
        self.in_progress_ttl_seconds = in_progress_ttl_seconds
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self._is_processing: bool = False
        self._processing_lock: Optional[threading.Lock] = None
        self.enable_ecs_scalein_protection = enable_ecs_scalein_protection
        self._ecs_scalein_protection_manager_kwargs = (
            ecs_scalein_protection_manager_kwargs or {}
        )
        self.logger = logger.bind(
            queue_name=self.queue_name, queue_url=self.queue.url
        )

    @property
    def is_processing_message(self) -> bool:
        """Flag for if message is currently being processed.

        Returns
        -------
        bool
            Whether this consumer instance is currently processing a message.

        """
        if not self.is_running:
            return False

        if not self._processing_lock:
            raise ConsumerError("Running, but _processing_lock not defined!")

        return self._processing_lock.locked()

    def _process_message(self, message: Message) -> ResultT:
        self.logger.info(
            "Starting processing message, message_id={}", message.message_id
        )
        try:
            body = deserialise_message_body(message.body)
            request_id = body.get("request_id")
            message_id = message.message_id
            serialised_message = sqs_message_to_dict(message)
        except Exception as exp:
            raise ConsumerUnretryableError(
                f"Error decoding message: {str(exp)}"
            ) from exp

        try:
            self.ddb_client.in_progress_put(
                self.in_progress_ttl_seconds,
                message_id=message_id,
                serialised_message=serialised_message,
                request_id=request_id,
            )
        except Exception as exp:
            raise ConsumerRetryableError(
                f"Error setting in_progress ddb status: {str(exp)}"
            ) from exp

        self.logger.info(
            "Calling compute function message_id={}", message.message_id
        )
        try:
            result = self.compute_result(body, message_id)
        except self.non_retryable_errors as exp:  # type: ignore
            raise ConsumerUnretryableError(
                f"Error computing result: {str(exp)}"
            ) from exp

        self.ddb_client.result_put(
            result=result,
            message_id=message_id,
            serialised_message=serialised_message,
            request_id=request_id,
        )
        return result

    def _consume_messages_wrapped(self):
        try:
            self._consume_messages()
        except Exception as exp:
            self.logger.opt(exception=True).critical(
                "Uncaught exception: {}", str(exp)
            )
            raise exp

    def _delete_message(self, message: Message) -> bool:
        try:
            message.delete()
        except Exception as exp:
            self.logger.opt(exception=True).error(
                "Failed to delete message with message_id={}: {}",
                message.message_id,
                str(exp),
            )
            return False

        self.logger.info(
            "Successfuly processed message with message_id={}",
            message.message_id,
        )
        return True

    def _process_message_wrapped(self, message: Message) -> Optional[ResultT]:
        result = None
        try:
            result = self._process_message(message)
        except ConsumerUnretryableError as exp:
            self.logger.opt(exception=True).error(
                "Unretryable error processing message w/ id={}: {}",
                message.message_id,
                str(exp),
            )
            self.ddb_client.error_put(
                message_id=message.message_id,
                exp=exp,
                serialised_message=sqs_message_to_dict(message),
            )
            self._delete_message(message)
        except (
            ConsumerRetryableError,
            Exception,
        ) as exp:  # Retry generic exp for now
            self.logger.opt(exception=True).error(
                "Retryable error processing message w/ id={}: {}",
                message.message_id,
                str(exp),
            )
        else:
            self._delete_message(message)
            self.logger.info(
                "Successfuly processed message with message_id={}",
                message.message_id,
            )
        return result

    def _consume_messages(self):
        while not self._stop_event.is_set():  # type: ignore
            messages = self.queue.receive_messages(
                MaxNumberOfMessages=1,
                WaitTimeSeconds=self.queue_wait_time_seconds,
            )
            if not messages:
                continue

            message = messages[0]
            self.logger.info(
                "Received message with message_id={}", message.message_id
            )

            try:
                ecs_prot_cm = (
                    ECSScaleInProtectionManager(
                        **self._ecs_scalein_protection_manager_kwargs
                    )
                    if self.enable_ecs_scalein_protection
                    else contextlib.nullcontext()
                )
                heartbeat_cm = Heartbeat(
                    queue_url=self.queue.url,
                    receipt_handle=message.receipt_handle,
                    visibility_timeout=self.heartbeat_visibility_timeout,
                    interval=self.heartbeat_interval,
                    message_id=message.message_id,
                    **self._boto3_sqs_resource_kwargs,
                )
                with (
                    self.logger.contextualize(message_id=message.message_id),
                    heartbeat_cm,
                    ecs_prot_cm,
                    self._processing_lock,  # type: ignore
                ):
                    # Internal exceptions raised by processes_message
                    # should be handled inside processes_message_wrapped
                    _ = self._process_message_wrapped(message)

            except HeartbeatStopTimeoutError as exp:
                self.logger.opt(exception=True).warning(
                    "Heartbeat thread didn't exit correctly: {}",
                    str(exp),
                )
            except ECSScaleInProtectionManagerError as exp:
                self.logger.opt(exception=True).warning(
                    "Error in ECS protection manager {}",
                    str(exp),
                )

        self.logger.info("Recieved stop event")

    @property
    def is_running(self) -> bool:
        """Check if this Consumer is consuming.

        Returns
        -------
        bool
            Whether this Consumer is consuming.

        """
        if not self._thread:
            return False

        return self._thread.is_alive()

    def start_consuming(
        self, *, delay_seconds: Optional[float] = None
    ) -> None:
        """Start the consume thread.

        Parameters
        ----------
        delay_seconds: float, optional
            Optional amount of time to wait before main thread returns,
            in order to allow consumer thread to start.

        """
        if self.is_running:
            raise ConsumerAlreadyConsumingError(
                "Already consuming, "
                f"thread_ident={self._thread.ident}"  # type: ignore
            )

        self._stop_event = threading.Event()
        self._processing_lock = threading.Lock()
        self._thread = threading.Thread(target=self._consume_messages_wrapped)
        self.logger = self.logger.bind(
            consumer_thread_ident=self._thread.ident
        )
        self.logger.debug("Starting consume...")
        self._thread.start()
        self.logger.info("Started consume, thread_ident={}")
        if delay_seconds:
            time.sleep(delay_seconds)

    def stop_consuming(self, timeout: float = 10) -> None:
        """Stop the consume thread.

        Parameters
        ----------
        timeout : int
            The timeout to pass to the Thread.join.

        Raises
        ------
        ConsumerStopTimeoutError
            If thread did not stop cleanly within the alloted timeout.

        """
        if self._thread and self.is_running:
            self.logger.info("Stopping consume")
            self._stop_event.set()  # type: ignore
            self._thread.join(timeout=timeout)

            if self._thread.is_alive():
                raise ConsumerStopTimeoutError(
                    f"Thread join hit timeout after {timeout} seconds"
                )

            self._thread = None
            self._stop_event.clear()  # type: ignore
            self._stop_event = None
            self._processing_lock = None


def _check_compute_result_callable(func: ComputeResultCallableT) -> None:
    sig = inspect.signature(func)
    params = sig.parameters

    kw_only_without_default = {
        k: p
        for k, p in params.items()
        if p.kind is p.KEYWORD_ONLY and p.default is p.empty
    }
    if kw_only_without_default:
        raise ValueError(
            "Callable with keyword only arguments without default not allowed"
            f" signature {sig}"
        )

    expected_num_args = len(typing.get_args(ComputeResultCallableT)[0])
    if len(params) < expected_num_args:
        raise ValueError(
            f"compute_result callable should have at least {expected_num_args}"
            f" args got {len(params)} with signature {sig}"
        )
