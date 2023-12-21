import io
import os
import tempfile
from typing import Optional

import boto3
from botocore.exceptions import ClientError as BotocoreClientError
from mypy_boto3_s3.service_resource import S3ServiceResource

from ..exceptions import AwaitingResult
from ._io import JsonT, load_json_from_binary
from .base import BaseResultFromStorageClient


class S3NoSuchKeyError(Exception):
    """For S3 errors where key not found."""


class S3ResultClient(BaseResultFromStorageClient):
    def __init__(
        self,
        *,
        bucket: str,
        key_prefix: Optional[str] = None,
        temp_dir: Optional[str] = None,
    ):
        self.s3: S3ServiceResource = boto3.resource("s3")

        self.bucket_name = bucket
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.key_prefix = key_prefix

        self.temp_dir = temp_dir

    def message_id_to_key(self, message_id: str) -> str:
        key_prefix = self.key_prefix or ""
        return f"{key_prefix}{message_id}"

    def result_get(self, message_id: str) -> JsonT:
        key = self.message_id_to_key(message_id)
        try:
            return self._get_file_from_s3(key)
        except S3NoSuchKeyError as exp:
            raise AwaitingResult(str(exp)) from exp

    def result_exists(self, message_id: str) -> bool:
        key = self.message_id_to_key(message_id)
        obj = self.bucket.Object(key)
        try:
            obj.load()
        except BotocoreClientError as exp:
            if exp.response["Error"]["Code"] == "404":  # type: ignore
                return False
            raise

        return True

    def _get_file_from_s3(
        self,
        key: str,
        **kwargs,
    ) -> JsonT:
        """Read file at path from S3."""
        obj = self.bucket.Object(key)
        try:
            obj.load()
        except BotocoreClientError as exp:
            if exp.response["Error"]["Code"] == "404":  # type: ignore
                # The object does not exist, but everything else OK
                raise S3NoSuchKeyError(str(exp)) from exp
            raise

        tmpdir = tempfile.mkdtemp(prefix=".", dir=self.temp_dir)
        local_path = os.path.join(tmpdir, obj.key.replace(os.sep, "_"))

        try:
            obj.download_file(local_path, **kwargs)
            with io.open(local_path, "rb") as _fp:
                return load_json_from_binary(_fp)
        finally:
            if os.path.isfile(local_path):
                os.remove(local_path)
            if os.path.isdir(tmpdir):
                os.rmdir(tmpdir)
