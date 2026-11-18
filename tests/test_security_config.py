"""S-01 / S-08: secrets come from configuration, never from code defaults."""
import base64

import pytest
from pydantic import ValidationError

from app.core.config import Settings

VALID_KEY = base64.urlsafe_b64encode(b"k" * 32).decode()
VALID_SECRET = "s" * 48


def _settings(**overrides):
    values = {
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "JWT_SECRET": VALID_SECRET,
        "ENCRYPTION_KEY": VALID_KEY,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_jwt_secret_is_required(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL="sqlite://", ENCRYPTION_KEY=VALID_KEY)


def test_jwt_secret_must_be_long(monkeypatch):
    with pytest.raises(ValidationError):
        _settings(JWT_SECRET="SUPER_SECRET_KEY")


def test_encryption_key_is_required(monkeypatch):
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL="sqlite://", JWT_SECRET=VALID_SECRET)


def test_encryption_key_must_decode_to_32_bytes():
    with pytest.raises(ValidationError):
        _settings(ENCRYPTION_KEY="dev-key")


def test_encryption_key_bytes_are_exposed():
    assert _settings().encryption_key_bytes == b"k" * 32


def test_public_register_disabled_by_default():
    assert _settings().ALLOW_PUBLIC_REGISTER is False


def test_cors_origins_parsed_from_comma_list():
    s = _settings(CORS_ORIGINS="http://a.test, http://b.test")
    assert s.cors_origins_list == ["http://a.test", "http://b.test"]


def test_hardcoded_secret_is_gone_from_auth_module():
    import app.core.auth as auth_module

    assert not hasattr(auth_module, "SECRET_KEY")
