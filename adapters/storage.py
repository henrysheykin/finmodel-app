"""File storage for delivered models: local disk (dev, single host) or S3-compatible buckets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol

KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,250}$")


def _check_key(key: str) -> str:
    if not KEY_RE.match(key) or ".." in key.split("/"):
        raise ValueError(f"invalid storage key {key!r}")
    return key


class Storage(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...
    def delete(self, key: str) -> None: ...


class LocalStorage:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        p = (self.root / _check_key(key)).resolve()
        if self.root not in p.parents:
            raise ValueError(f"storage key escapes the root: {key!r}")
        return p

    def put(self, key: str, data: bytes, content_type: str) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(p)  # atomic: readers never see half a file

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)


class S3Storage:
    """S3 / R2 / MinIO. The boto3 client is injected (tests pass a fake; prod builds a real one)."""

    def __init__(self, bucket: str, client):
        self.bucket, self.client = bucket, client

    @classmethod
    def from_env(cls, bucket: str, endpoint_url: str = "") -> S3Storage:
        import boto3  # optional dependency: only needed when STORAGE_BACKEND=s3

        return cls(bucket, boto3.client("s3", endpoint_url=endpoint_url or None))

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(Bucket=self.bucket, Key=_check_key(key), Body=data, ContentType=content_type)

    def get(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=_check_key(key))["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=_check_key(key))
            return True
        except Exception as exc:  # botocore ClientError 404
            if getattr(exc, "response", {}).get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
                return False
            raise

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=_check_key(key))


def make_storage(backend: str, storage_dir: str, bucket: str = "", endpoint_url: str = "") -> Storage:
    if backend == "local":
        return LocalStorage(storage_dir)
    if backend == "s3":
        if not bucket:
            raise RuntimeError("STORAGE_BACKEND=s3 needs S3_BUCKET")
        return S3Storage.from_env(bucket, endpoint_url)
    raise RuntimeError(f"unknown STORAGE_BACKEND {backend!r}")
