"""Client for interacting with DynamoDB."""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import time
from decimal import Decimal
from typing import Any, Literal, Optional

import boto3
from loguru import logger
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from .exceptions import (
    AwaitingResultTimeoutError,
    DDBError,
    ExpiredItemError,
    KeyAlreadyExistsError,
    KeyNotFoundError,
    ResultErrorStatusError,
    ResultInProgressStatusError,
    ResultMissingError,
    UnparseableItemError,
)
from .types import (
    JsonStrT,
    JsonT,
    MessageAsDictT,
    MessageIdT,
    ResultStatus,
    ResultT,
)

_DDBPollContinueErrors = (KeyNotFoundError, ResultInProgressStatusError)
_KeyT = dict[Literal["message_id"], MessageIdT]


class DynamoDBClient:
    """Client for interacting with DDB results."""

    def __init__(self, table_name: str, **boto3_ddb_resource_kwargs):
        """Get a new DynamoDBClient.

        Parameters
        ----------
        table_name : str
            The DynamoDB table name.

        """
        self.table_name = table_name
        self.dynamodb: DynamoDBServiceResource = boto3.resource(
            "dynamodb", **boto3_ddb_resource_kwargs
        )
        self.table: Table = self.dynamodb.Table(self.table_name)
        self.logger = logger.bind(table_name=self.table_name)

    @staticmethod
    def _message_id_to_key(message_id: MessageIdT) -> _KeyT:
        return {"message_id": message_id}

    def result_poll(
        self,
        message_id: MessageIdT,
        timeout_seconds: float = 5,
        poll_time_seconds: float = 0.1,
        return_request_id: bool = False,
    ) -> ResultT | tuple[ResultT, str | None]:
        """Poll until result ready and available.

        Parameters
        ----------
        message_id : str
            The message ID to look for.
        timeout_seconds : float
            The number of seconds to wait before timing-out.
        poll_time_seconds : float
            The interval with which to poll for result.
        return_request_id : bool
            Whether to return the request_id aswell as the result.

        Returns
        -------
        dict or tuple of (dict, request_id)
            The final result

        Raises
        ------
        AwaitingResultTimeoutError :
            If polling timeout is reached.

        """
        timeout = time.time() + timeout_seconds

        while time.time() < timeout:
            try:
                return self.result_get(message_id, return_request_id)
            except _DDBPollContinueErrors:
                time.sleep(poll_time_seconds)

        raise AwaitingResultTimeoutError("Timeout reached.")

    def item_exists(self, message_id: MessageIdT) -> bool:
        """Check if item exists for this message id.

        Parameters
        ----------
        message_id : str

        Returns
        -------
        bool
            Whether the item exists.

        """
        key = self._message_id_to_key(message_id)
        response = self.table.get_item(Key=key, ConsistentRead=True)
        item = response.get("Item", {})
        return bool(item)

    def item_get(
        self,
        message_id: MessageIdT,
        raise_for_expiry: bool = True,
    ) -> DynamoDBItem:
        """Get the DDB item for this message_id.

        Parameters
        ----------
        message_id : str
            The SQS message_id.
        raise_for_expiry : bool
            Check for item expiry and raise if it is expired.

        Returns
        -------
        DynamoDBItem
            The fetched item as a DynamoDBItem obj.

        Raises
        ------
        UnparseableItemError
            If the item found can't be used to nstantiate a DynamoDBItem.
        KeyNotFoundError
            If there is no object corresponding to message_id.
        ExpiredItemError
            If the found item is expired.

        """
        key = self._message_id_to_key(message_id)
        response = self.table.get_item(Key=key, ConsistentRead=True)
        item = response.get("Item", {})
        if not item:
            raise KeyNotFoundError(f"No item found for key={key}")

        self.logger.debug("Got item={} for key={}", item, key)
        try:
            item_obj = DynamoDBItem.from_get_item(item)
        except Exception as exp:
            raise UnparseableItemError(
                f"Unable to parse {item=} with {key=}: "
                f"{type(exp)} - {str(exp)}"
            ) from exp

        if raise_for_expiry and item_obj.is_expired():
            raise ExpiredItemError(
                f"Item with {key=} has expired, expiry={item_obj.expiration}"
            )

        return item_obj

    def result_get(
        self, message_id: MessageIdT, return_request_id: bool = False
    ) -> ResultT | tuple[ResultT, str | None]:
        """Get the result for this message id.

        Parameters
        ----------
        message_id : str
            The SQS message_id to look for.
        return_request_id : bool
            Whether to return the request_id aswell as the result.

        Returns
        -------
        dict or tuple of (dict, request_id)

        Raises
        ------
        ResultMissingError
            If an item exists at message_id, but without result attribute.
        ResultErrorStatusError
            If an item exists at message_id, but it has ERROR status.
        ResultInProgressStatusError
            If the result computation is still in progress.

        """
        item_obj = self.item_get(message_id)

        self.logger.debug("Parsed item={}", item_obj)
        if item_obj.status == ResultStatus.ERROR:
            raise ResultErrorStatusError(
                f"Got item for {message_id=}, but has error status"
                f"error={item_obj.error}"
            )

        if item_obj.status in [
            ResultStatus.IN_PROGRESS,
            ResultStatus.SUBMITTED,
        ]:
            raise ResultInProgressStatusError(
                f"Result for {message_id=} is still in progress, "
                f"status={item_obj.status}"
            )

        if item_obj.result is None:
            raise ResultMissingError(
                f"Item is missing result for {message_id=} "
                f"result status={item_obj.status}"
            )

        result = item_obj.result
        request_id = item_obj.request_id
        self.logger.info(
            "Got result, message_id={}, request_id={}", message_id, request_id
        )
        if return_request_id:
            return result, request_id
        return result

    def status_get(self, message_id: MessageIdT) -> ResultStatus:
        """Get the status of this message_id.

        Parameters
        ----------
        message_id : str

        Returns
        -------
        ResultStatus

        """
        try:
            item_obj = self.item_get(message_id)
        except (ExpiredItemError, UnparseableItemError):
            return ResultStatus.ERROR

        return item_obj.status

    def result_exists(self, message_id: MessageIdT) -> bool:
        """Check if this result exists.

        Parameters
        ----------
        message_id : str

        Returns
        -------
        bool
            Whether the result exists.

        """
        try:
            self.result_get(message_id)
        except DDBError:
            return False

        return True

    def item_put(
        self,
        item: Optional[DynamoDBItem] = None,
        allow_overwrite: bool = True,
        **ddb_item_kwargs,
    ) -> None:
        """Put item in DynamoDB table.

        Parameters
        ----------
        item : DynamoDBItem
        allow_overwrite : bool
            Whether to allow overwrite of pre-existing key.

        Raises
        ------
        KeyAlreadyExistsError :
            If allow_overwrite=false & key already exists.

        """
        item = item or DynamoDBItem(  # pylint: disable=missing-kwoa
            **ddb_item_kwargs
        )

        message_id = item.message_id
        if not allow_overwrite and self.item_exists(message_id):
            raise KeyAlreadyExistsError(
                f"Item with {message_id=} already found and {allow_overwrite=}"
            )
        _puttable = item.to_puttable()
        self.table.put_item(Item=_puttable)
        self.logger.info(
            "Successfully put item in DynamoDB message_id={}, "
            "status={} request_id={}",
            message_id,
            item.status,
            item.request_id,
        )

    def status_put(
        self,
        *,
        status: ResultStatus,
        message_id: MessageIdT,
        request_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        error: Optional[str] = None,
        serialised_message: Optional[MessageAsDictT] = None,
    ) -> None:
        """Put a status item for key as message_id.

        Parameters
        ----------
        status : ResultStatus
            The status to put.
        message_id : str
            The message_id key.
        request_id: str, optional
            The corresponding request_id.
        ttl_seconds : int or None
            The expiry ttl for this status item.
        error : str, optional
            The error message string, for error statuses.
        serialised_message : dict, optional
            The serialised message.

        Raises
        ------
        ValueError

        """
        if status == ResultStatus.SUCCESS:
            raise ValueError(
                "This method cannot be used to set result status success"
            )
        if error and status != ResultStatus.ERROR:
            raise ValueError(
                f"Can only set error if status=ERROR, got {status=}, {error=}"
            )

        expiration = _expiration_from_ttl(ttl_seconds) if ttl_seconds else None
        item = DynamoDBItem(
            result=None,
            request_id=request_id,
            message_id=message_id,
            status=status,
            serialised_message=serialised_message,
            error=error,
            expiration=expiration,
        )
        self.item_put(item)

    def in_progress_put(
        self,
        ttl_seconds: Optional[int],
        **kwargs,
    ) -> None:
        """Put in_progress flag for item.

        Parameters
        ----------
        ttl_seconds : int
            Time to live for this item.
        kwargs : Any
            Passed onto the status_put method.

        """
        self.status_put(
            status=ResultStatus.IN_PROGRESS,
            error=None,
            ttl_seconds=ttl_seconds,
            **kwargs,
        )

    def submitted_put(
        self,
        ttl_seconds: Optional[int],
        **kwargs,
    ) -> None:
        """Put submitted flag for item.

        Parameters
        ----------
        ttl_seconds : int
            Time to live for this item.
        kwargs : Any
            Passed onto the status_put method.

        """
        self.status_put(
            status=ResultStatus.SUBMITTED,
            error=None,
            ttl_seconds=ttl_seconds,
            **kwargs,
        )

    def error_put(
        self,
        exp: Optional[Exception | str] = None,
        **kwargs,
    ) -> None:
        """Put error flag for item.

        Parameters
        ----------
        exp : Exception or str
            Exception message for the error.
        kwargs : Any
            Passed onto the status_put method.

        """
        if not exp:
            error = "Unknown error"
        elif isinstance(exp, str):
            error = exp
        else:  # Exception
            error = f"{type(exp)}: {str(exp)}"

        self.status_put(status=ResultStatus.ERROR, error=error, **kwargs)

    def result_put(
        self,
        *,
        message_id: MessageIdT,
        result: ResultT,
        serialised_message: Optional[MessageAsDictT] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Put the successful result into DDB table.

        Parameters
        ----------
        message_id : str
        result : dict (json.dumps serialisable)
        serialised_message : dict

        """
        item = DynamoDBItem(
            message_id=message_id,
            status=ResultStatus.SUCCESS,
            result=result,
            serialised_message=serialised_message,
            request_id=request_id,
        )
        self.item_put(item)


def _utcnow() -> dt.datetime:
    dt_ = dt.datetime.now(dt.timezone.utc)
    rounded_down = dt_.replace(microsecond=0)
    return rounded_down


def _expiration_from_ttl(
    ttl_seconds: int, dt_: Optional[dt.datetime] = None
) -> dt.datetime:
    dt_ = dt_ or _utcnow()
    ttl = dt.timedelta(seconds=ttl_seconds)
    return dt_ + ttl


def _dt_to_ts(dt_: dt.datetime) -> int:
    if not dt_.tzinfo:
        raise ValueError("Got naive datetime")

    return int(round(dt_.timestamp()))


def _ts_to_dt(
    timestamp: float | Decimal, tzinfo: dt.tzinfo = dt.timezone.utc
) -> dt.datetime:
    timestamp = float(timestamp)
    return dt.datetime.fromtimestamp(timestamp, tzinfo)


@dataclasses.dataclass(kw_only=True)
class DynamoDBItem:
    """Class encapsulating a DynamoDB result item."""

    message_id: MessageIdT  # Primary key for ddb
    request_id: Optional[str] = None
    status: ResultStatus = ResultStatus.SUCCESS
    result: Optional[ResultT]
    # created_at: dt.datetime = dataclasses.field(default_factory=_utcnow)
    updated_at: dt.datetime = dataclasses.field(default_factory=_utcnow)
    serialised_message: Optional[MessageAsDictT] = None
    error: Optional[str] = None
    expiration: Optional[dt.datetime] = None  # ttl

    def __post_init__(self):
        if self.status == ResultStatus.SUCCESS and self.error:
            raise ValueError("Cannot set error message and status=SUCCESS")
        if self.status == ResultStatus.SUCCESS and self.result is None:
            raise ValueError("Successful result should not be none")
        if self.result and self.expiration:
            raise ValueError("Successful result should not expire")

    def to_puttable(
        self,
    ) -> dict[str, str | JsonT | MessageAsDictT | None | int]:
        """Get a DDB puttable version of this Item."""
        out = {
            "message_id": self.message_id,
            "status": self.status,
            # "created_at": _dt_to_ts(self.created_at),
            "updated_at": _dt_to_ts(self.updated_at),
        }
        if self.result:
            out["result"] = _serialise_result(self.result)
        if self.serialised_message:
            out["serialised_message"] = self.serialised_message
        if self.error:
            out["error"] = self.error
        if self.expiration:
            out["expiration"] = _dt_to_ts(self.expiration)
        if self.request_id:
            out["request_id"] = self.request_id
        return out

    @classmethod
    def from_get_item(cls, item: dict[str, Any]) -> DynamoDBItem:
        """Instantiate a DynamoDBItem from a .get_item call.

        Parameters
        ----------
        item : dict

        Returns
        -------
        DynamoDBItem

        """
        if result := item.get("result"):
            result = _deserialise_result(result)

        if expiration := item.get("expiration"):
            expiration = _ts_to_dt(expiration)

        return cls(
            message_id=item["message_id"],
            result=result,
            status=item["status"],
            # created_at=_ts_to_dt(item["created_at"]),
            updated_at=_ts_to_dt(item["updated_at"]),
            serialised_message=item.get("serialised_message"),
            error=item.get("error"),
            expiration=expiration,
            request_id=item.get("request_id"),
        )

    def is_expired(self) -> bool:
        """Check whether this item is expired.

        Returns
        -------
        bool
            Whether or not this Item is expired.

        """
        if self.status == ResultStatus.SUCCESS:
            return False

        if not self.expiration:
            return False

        return _utcnow() > self.expiration


def _serialise_result(result: ResultT) -> JsonStrT:
    return json.dumps(result)


def _deserialise_result(json_str: JsonStrT) -> ResultT:
    return json.loads(json_str)
