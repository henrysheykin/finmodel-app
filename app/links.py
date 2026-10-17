"""Signed, expiring download links.

token = <artifact_id>.<expires_unix>.<signature>, signature = HMAC-SHA256(secret, "dl:<id>:<exp>")
truncated to 32 bytes, base64url. Nothing is stored: changing SECRET_KEY revokes every link.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time


class LinkError(ValueError):
    pass


def _sig(secret: str, artifact_id: str, expires: int) -> str:
    mac = hmac.new(secret.encode(), f"dl:{artifact_id}:{expires}".encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).rstrip(b"=").decode()


def sign(secret: str, artifact_id: str, ttl_seconds: int, now: float | None = None) -> str:
    expires = int((now if now is not None else time.time()) + ttl_seconds)
    return f"{artifact_id}.{expires}.{_sig(secret, artifact_id, expires)}"


def verify(secret: str, token: str, now: float | None = None) -> str:
    """Return the artifact id if the token is authentic and not expired."""
    try:
        artifact_id, exp_s, sig = token.split(".")
        expires = int(exp_s)
    except ValueError:
        raise LinkError("malformed link") from None
    if not hmac.compare_digest(sig, _sig(secret, artifact_id, expires)):
        raise LinkError("invalid link")
    if (now if now is not None else time.time()) > expires:
        raise LinkError("link expired")
    return artifact_id
