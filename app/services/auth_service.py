"""Password verification and signed bearer-token helpers."""

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.config import settings


class InvalidTokenError(Exception):
    """Raised when an access token is invalid or expired."""


def verify_password(password: str, encoded_password: str) -> bool:
    """Verify a password stored in the app's PBKDF2 format."""
    try:
        algorithm, iterations, salt, expected_digest = encoded_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
        return hmac.compare_digest(digest, expected_digest)
    except (ValueError, TypeError):
        return False


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _base64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(user_id: int, role: int) -> tuple[str, int]:
    """Create a signed JWT-compatible access token."""
    expires_in = settings.auth_token_expire_hours * 60 * 60
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + expires_in,
    }
    segments = [
        _base64url_encode(json.dumps(header, separators=(",", ":")).encode()),
        _base64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
    ]
    signing_input = ".".join(segments).encode()
    signature = hmac.new(
        settings.auth_secret_key.encode(), signing_input, hashlib.sha256
    ).digest()
    return f"{'.'.join(segments)}.{_base64url_encode(signature)}", expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate a token signature and expiry, then return its claims."""
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}".encode()
        expected_signature = hmac.new(
            settings.auth_secret_key.encode(), signing_input, hashlib.sha256
        ).digest()
        supplied_signature = _base64url_decode(signature_segment)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            raise InvalidTokenError("Invalid access token")

        header = json.loads(_base64url_decode(header_segment))
        payload = json.loads(_base64url_decode(payload_segment))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise InvalidTokenError("Invalid access token")
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise InvalidTokenError("Access token has expired")
        int(payload["sub"])
        return payload
    except InvalidTokenError:
        raise
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise InvalidTokenError("Invalid access token") from exc
