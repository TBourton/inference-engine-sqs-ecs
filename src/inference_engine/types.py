"""Collection of types."""
# pylint: disable=invalid-name
from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Literal

JsonStrT = str
JsonT = Any
ResultT = JsonT
MessageBodyT = JsonT
MessageIdT = str

MessageAsDictT = dict[
    Literal[
        "body",
        "attributes",
        "md5_of_body",
        "md5_of_message_attributes",
        "message_attributes",
        "message_id",
    ],
    str | dict,
]


class ResultStatus(str, Enum):
    """Class for indicating result status."""

    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"


ComputeResultCallableT = Callable[[MessageBodyT, MessageIdT], ResultT]
