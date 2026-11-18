"""S-03: the audit actor comes from the verified JWT, never from request headers."""
import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.auth import create_access_token, create_refresh_token
from app.core.database import AsyncSessionLocal
from app.middleware.audit import AuditLogMiddleware
from app.models.audit import AuditLog


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(AuditLogMiddleware)

    @app.get("/probe/{tag}")
    async def probe(tag: str):
        return {"tag": tag}

    return app


async def _call(headers: dict) -> AuditLog:
    tag = uuid.uuid4().hex
    async with AsyncClient(transport=ASGITransport(app=_app()), base_url="http://test") as client:
        r = await client.get(f"/probe/{tag}", headers=headers)
        assert r.status_code == 200
    async with AsyncSessionLocal() as s:
        rows = (await s.execute(select(AuditLog).where(AuditLog.resource == f"/probe/{tag}"))).scalars().all()
    assert len(rows) == 1
    return rows[0]


@pytest.mark.asyncio
async def test_spoofed_identity_headers_are_ignored():
    log = await _call({"X-User-ID": "admin", "X-Impersonator-ID": "root"})
    assert log.actor_id == "anonymous"
    assert log.user_id == "anonymous"
    assert log.impersonator_id is None


@pytest.mark.asyncio
async def test_actor_comes_from_verified_access_token():
    user_id = str(uuid.uuid4())
    token = create_access_token({"sub": user_id})
    log = await _call({"Authorization": f"Bearer {token}", "X-User-ID": "someone-else", "User-Agent": "pytest-ua"})
    assert log.actor_id == user_id
    assert log.user_agent == "pytest-ua"
    assert log.ip


@pytest.mark.asyncio
async def test_impersonation_comes_from_token_claim():
    token = create_access_token({"sub": "target-user", "imp": "admin-user"})
    log = await _call({"Authorization": f"Bearer {token}"})
    assert log.actor_id == "target-user"
    assert log.impersonator_id == "admin-user"


@pytest.mark.asyncio
async def test_invalid_or_refresh_tokens_are_anonymous():
    forged = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.invalid"
    assert (await _call({"Authorization": f"Bearer {forged}"})).actor_id == "anonymous"
    refresh = create_refresh_token({"sub": "x"})
    assert (await _call({"Authorization": f"Bearer {refresh}"})).actor_id == "anonymous"
