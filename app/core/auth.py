"""JWT creation and verification.

Every token carries a ``type`` claim (``access`` or ``refresh``) and
``verify_token`` only accepts the type the caller expects, so a long-lived
refresh token can never be used as an access token.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
TokenType = Literal["access", "refresh"]


def _encode(data: dict, token_type: TokenType, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expires_delta, "type": token_type})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    return _encode(data, "access", delta)


def create_refresh_token(data: dict, jti: Optional[str] = None) -> str:
    claims = {**data, "jti": jti or uuid.uuid4().hex}
    return _encode(claims, "refresh", timedelta(days=settings.REFRESH_TOKEN_DAYS))


def verify_token(token: str, expected_type: TokenType = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload
