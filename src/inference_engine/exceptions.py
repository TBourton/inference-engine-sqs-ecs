"""Exceptions for the inference_engine package."""


class BaseError(Exception):
    """Base exception for this library."""


class SQSConnectionError(BaseError):
    """Exception raised for SQS connection errors."""


# DDB
class DDBError(BaseError):
    """Base DDB client error."""


class KeyNotFoundError(DDBError):
    """For when Key does not exist in DB."""


class KeyAlreadyExistsError(DDBError):
    """For when Key already exists and denied operation tries to overwrite."""


class ResultMissingError(DDBError):
    """For when key does exist in DB, but result is missing."""


class ResultErrorStatusError(DDBError):
    """To be raised when result has status ERROR."""


class ResultInProgressStatusError(DDBError):
    """To be raised when result has status IN_PROGRESS."""


class UnparseableItemError(DDBError):
    """To be raised when DDB Item cannot be parsed."""


class AwaitingResultTimeoutError(DDBError, TimeoutError):
    """Raised when result poll times out."""


class ExpiredItemError(DDBError):
    """Raised when DDB item expired."""


# Producer
class ProducerError(BaseError):
    """Base Producer error."""


# Consumer
class ConsumerError(BaseError):
    """Base Consumer error."""


class HeartbeatError(ConsumerError):
    """Base Heartbeat error."""


class HeartbeatStopTimeoutError(ConsumerError, TimeoutError):
    """For timeout of heartbeat stop."""


class ECSScaleInProtectionManagerError(ConsumerError):
    """Base ECSScaleInProtectionManager error."""


class ECSScaleInProtectionManagerRequestError(ConsumerError):
    """For ECSScaleInProtectionManager errors from requests."""


class ECSScaleInProtectionManagerAgentError(ConsumerError):
    """For ECSScaleInProtectionManager errors from requests."""


class ConsumerRetryableError(ConsumerError):
    """For errors that constitute a retry (500s).

    This should NOT trigger a message.delete.

    """


class ConsumerUnretryableError(ConsumerError):
    """For errors that do not constitute a retry (400s).

    This should trigger a message.delete.

    """


class ConsumerStopTimeoutError(ConsumerError, TimeoutError, RuntimeError):
    """For timeout of consumer stop."""


class ConsumerAlreadyConsumingError(ConsumerError):
    """For if already consuming."""
