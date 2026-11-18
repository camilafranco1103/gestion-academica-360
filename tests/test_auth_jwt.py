from datetime import timedelta

from app.core.auth import create_access_token, create_refresh_token, verify_token


def test_create_and_verify_token():
    token = create_access_token({"sub": "user123"})
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user123"
    assert decoded["type"] == "access"


def test_verify_invalid_token():
    assert verify_token("invalid.token.string") is None


def test_create_refresh_token():
    token = create_refresh_token({"sub": "user123"})
    decoded = verify_token(token, expected_type="refresh")
    assert decoded is not None
    assert decoded["sub"] == "user123"
    assert decoded["type"] == "refresh"
    assert decoded["jti"]


def test_refresh_token_is_rejected_as_access_token():
    """S-02: a 7-day refresh token must never authenticate API calls."""
    token = create_refresh_token({"sub": "user123"})
    assert verify_token(token) is None


def test_access_token_is_rejected_as_refresh_token():
    token = create_access_token({"sub": "user123"})
    assert verify_token(token, expected_type="refresh") is None


def test_token_signed_with_old_hardcoded_secret_is_rejected():
    """S-01: tokens forged with the previously hardcoded secret are invalid."""
    from jose import jwt

    forged = jwt.encode({"sub": "user123", "type": "access"}, "SUPER_SECRET_KEY", algorithm="HS256")
    assert verify_token(forged) is None


def test_verify_expired_token():
    expired = create_access_token({"sub": "user123"}, expires_delta=timedelta(hours=-1))
    assert verify_token(expired) is None
