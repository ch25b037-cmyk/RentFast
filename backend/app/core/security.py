"""Token, OTP and hash helpers."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from app.core.config import get_settings


def hash_value(value: str) -> str:
    return hmac.new(get_settings().secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()


def compare_value(value: str, digest: str) -> bool:
    return hmac.compare_digest(hash_value(value), digest)


def generate_numeric_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expires, "type": "access"}, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    if payload.get("type") != "access" or not payload.get("sub"):
        raise ValueError("Invalid access token")
    return str(payload["sub"])


def new_refresh_token() -> tuple[str, str]:
    return secrets.token_urlsafe(48), str(uuid4())
