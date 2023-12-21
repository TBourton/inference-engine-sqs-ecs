"""Producer."""
from __future__ import annotations

import dataclasses
import math
import typing
import uuid
from typing import Literal, Optional

from loguru import logger
from mypy_boto3_sqs.type_defs import SendMessageResultTypeDef

from .._sqs_base import _SQSBase, serialise_message_body
from ..dynamo_db_client import DynamoDBClient
from ..exceptions import ResultErrorStatusError, ResultMissingError
from ..types import JsonT, MessageIdT, ResultStatus, ResultT

MessageGroupIdModeT = Literal["global", "producer", "request"]

_DDB500Exps = (ResultMissingError, ResultErrorStatusError)


class Producer(_SQSBase):
    """Client for interacting with sqs."""

    def __init__(
        self,
        queue_name: str,
        *,
        message_group_id_mode: MessageGroupIdModeT = "global",
        timeout_seconds: float = 5 * 60,
        poll_time_seconds: float = 1,
        ddb_client: DynamoDBClient,
        **boto3_sqs_resource_kwargs,
    ):
        """Get a new Producer.

        Parameters
        ----------
        queue_name : str
            The name of the SQS queue.
        message_group_id_mode: MessageGroupIdModeT
            Creation method for the MessageGroupID.
        timeout_seconds : float
            The timeout to set for DDB item ttl and for timing out on polling.
            This should be set to the maximum time of the longest running task
            consuming from the queue.
        poll_time_seconds : float
            The wait time to use for polling for result.
        ddb_client : DynamoDBClient
            The DynamoDBClient to use.
        kwargs : Any
            Kwargs passed onto the boto3 as boto3.resource("sqs", **kwargs).

        """
        super().__init__(
            queue_name=queue_name,
            ddb_client=ddb_client,
            **boto3_sqs_resource_kwargs,
        )

        if message_group_id_mode not in typing.get_args(MessageGroupIdModeT):
            raise ValueError(
                f"Invalid {message_group_id_mode=}, expected one of"
                f"{typing.get_args(MessageGroupIdModeT)}"
            )
        self.message_group_id_mode = message_group_id_mode
        self.poll_time_seconds = poll_time_seconds
        self.timeout_seconds = timeout_seconds
        self.logger = logger.bind(queue_name=self.queue_name)

    def _message_group_id(self, request_id: str) -> str:
        if self.message_group_id_mode == "global":
            return "default_message_group_id"
        if self.message_group_id_mode == "request":
            return request_id
        if self.message_group_id_mode == "producer":
            return str(id(self))

        raise ValueError(f"Unknown {self.message_group_id_mode=}")

    def post(
        self,
        message_body: JsonT,
        request_id: Optional[str] = None,
    ) -> Response:
        """Send message to the queue and block until result is ready.

        Parameters
        ----------
        message_body : dict
            json.dumps-able dict.
        request_id : str, optional
            The request_id to attach, if none, one is automatically created.

        Returns
        -------
        Response

        """
        message_id = self.post_non_blocking(message_body, request_id)
        resp = self._poll_storage_and_block(message_id)
        self.logger.info(
            "Successfully got result from storage, message_id={}", message_id
        )

        return resp

    def post_non_blocking(
        self,
        message_body: JsonT,
        request_id: Optional[str] = None,
    ) -> MessageIdT:
        """Submit a message but do not block.

        Parameters
        ----------
        message_body : dict
            json.dumps-able dict.

        Returns
        -------
        str
            The message_id for the submitted job.

        """
        request_id = request_id or str(uuid.uuid4())
        message_body["request_id"] = request_id
        message_str = serialise_message_body(message_body)
        message_group_id = self._message_group_id(request_id)
        response: SendMessageResultTypeDef = self.queue.send_message(
            MessageBody=message_str,
            MessageGroupId=message_group_id,
        )
        message_id = response["MessageId"]
        self.ddb_client.submitted_put(
            ttl_seconds=int(math.ceil(self.timeout_seconds)),
            request_id=request_id,
            serialised_message=message_str,
            message_id=message_id,
        )
        self.logger.info(
            "Successfully submitted message, message_id={}, "
            "request_id={}, message_group_id={}",
            message_id,
            request_id,
            message_group_id,
        )
        return message_id

    def retrieve_result_status(self, message_id: MessageIdT) -> ResultStatus:
        """Check the status of the result for this message_id.

        Parameters
        ----------
        message_id : str
            The SQS message_id key for the desired result.

        Returns
        -------
        ResultStatus

        Raises
        ------
        KeyNotFoundError
            If no key found for message_id.

        """
        return self.ddb_client.status_get(message_id)

    def retrieve_result(self, message_id: MessageIdT) -> Response:
        """Retrieve the result for this message_id.

        Parameters
        ----------
        message_id : str
            The SQS message_id for the desired result.

        Returns
        -------
        Response

        """
        try:
            result, request_id = self.ddb_client.result_get(
                message_id, return_request_id=True
            )
        except _DDB500Exps as exp:
            return Response.from_exp(exp, message_id, 500)

        return Response(
            message_id=message_id, result=result, request_id=request_id
        )

    def _poll_storage_and_block(self, message_id: str) -> Response:
        try:
            result, request_id = self.ddb_client.result_poll(
                message_id,
                timeout_seconds=self.timeout_seconds,
                poll_time_seconds=self.poll_time_seconds,
                return_request_id=True,
            )
        except _DDB500Exps as exp:
            return Response.from_exp(exp, message_id, 500)
        except TimeoutError as exp:
            return Response.from_exp(exp, message_id, 500)

        return Response(
            message_id=message_id, result=result, request_id=request_id
        )


@dataclasses.dataclass(kw_only=True)
class Response:
    """Class encapsulating a post request Response."""

    message_id: MessageIdT
    request_id: Optional[str] = None
    status: ResultStatus = ResultStatus.SUCCESS
    status_code: int = 200
    result: Optional[ResultT]
    error: Optional[Exception] = None

    @classmethod
    def from_exp(
        cls, exp: Exception, message_id: MessageIdT, status_code: int
    ) -> Response:
        """Derive an ERROR status result based on client side raised exp.

        Parameters
        ----------
        exp : Exception
            The exception that caused the client side error.
        message_id : str
            The message_id for the error response.
        status_code : int
            The desired status_code.

        Returns
        -------
        Response

        """
        return Response(
            message_id=message_id,
            status=ResultStatus.ERROR,
            status_code=status_code,
            result=None,
            error=exp,
            # error=f"{type(exp).__name__} - {str(exp)}"
        )
