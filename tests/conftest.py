"""
Shared pytest configuration for Gestión Académica 360 tests.

The environment is pinned BEFORE any ``app`` import so that tests never touch
the developer database from ``.env`` and always run with test-only secrets.

Importing all models here ensures Base.metadata knows about every table
before any test calls Base.metadata.create_all(). This prevents
ForeignKey constraint failures when models like Carrera reference
tenants.id but Tenant hasn't been imported yet.

Also creates all tables in test.db (used by HTTP endpoint tests via
TestClient) so the audit middleware can log to audit_logs.
"""
import base64
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-jwt-secret-" + "x" * 48
os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(b"t" * 32).decode()
os.environ["ALLOW_PUBLIC_REGISTER"] = "false"

import pytest  # noqa: E402

import app.models  # noqa: E402,F401 — registers ALL models on Base.metadata

from sqlalchemy import create_engine  # noqa: E402
from app.models.base import Base  # noqa: E402

_sync_engine = create_engine("sqlite:///./test.db")
Base.metadata.create_all(_sync_engine)
_sync_engine.dispose()


@pytest.fixture(autouse=True)
def _reset_login_rate_limiter():
    """Login attempts are tracked in memory; isolate them per test."""
    from app.core.rate_limit import login_rate_limiter

    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()
