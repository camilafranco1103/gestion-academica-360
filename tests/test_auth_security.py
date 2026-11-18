"""Security behaviour of /api/auth (S-02, S-05, S-06, S-07, S-09, S-10, S-12)."""
import uuid

import bcrypt
import pyotp
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from app.models.rbac import Role
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.routers.auth import router as auth_router

PASSWORD = "Correcta123!"


@pytest_asyncio.fixture
async def ctx():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        tenant = Tenant(id=uuid.uuid4(), name="T1")
        alumno = Role(id=1, name="ALUMNO")
        s.add_all([tenant, alumno])
        await s.flush()
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="ana@test.com",
            nombre="Ana Test",
            hashed_password=bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode(),
        )
        s.add(user)
        await s.flush()
        s.add(UserRole(user_id=user.id, role_id=alumno.id))
        await s.commit()

    app = FastAPI()
    app.include_router(auth_router, prefix="/api/auth")

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, factory, user
    await engine.dispose()


async def _login(client, email="ana@test.com", password=PASSWORD, **extra):
    return await client.post("/api/auth/login", json={"email": email, "password": password, **extra})


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


# --- S-09: no backdoor -------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["user", "testuser"])
async def test_backdoor_usernames_do_not_get_tokens(ctx, email):
    client, _, _ = ctx
    r = await _login(client, email=email, password="anything")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_wrong_password_is_401(ctx):
    client, _, _ = ctx
    assert (await _login(client, password="incorrecta")).status_code == 401


@pytest.mark.asyncio
async def test_unknown_fields_rejected(ctx):
    client, _, _ = ctx
    r = await _login(client, tenant_id=str(uuid.uuid4()))
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_inactive_user_cannot_login(ctx):
    client, factory, user = ctx
    async with factory() as s:
        u = await s.get(User, user.id)
        u.activo = False
        await s.commit()
    assert (await _login(client)).status_code == 401


# --- S-02: refresh token is not an access token ------------------------------

@pytest.mark.asyncio
async def test_me_accepts_access_token_and_rejects_refresh_token(ctx):
    client, _, _ = ctx
    tokens = (await _login(client)).json()
    me = await client.get("/api/auth/me", headers=_bearer(tokens["access_token"]))
    assert me.status_code == 200
    assert me.json()["nombre"] == "Ana Test"
    assert (await client.get("/api/auth/me", headers=_bearer(tokens["refresh_token"]))).status_code == 401


# --- S-06: refresh rotation + logout -----------------------------------------

@pytest.mark.asyncio
async def test_refresh_rotates_tokens(ctx):
    client, _, _ = ctx
    first = (await _login(client)).json()
    r = await client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert r.status_code == 200
    second = r.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert (await client.get("/api/auth/me", headers=_bearer(second["access_token"]))).status_code == 200


@pytest.mark.asyncio
async def test_reusing_a_rotated_refresh_token_revokes_the_session(ctx):
    client, _, _ = ctx
    first = (await _login(client)).json()
    second = (await client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})).json()

    reuse = await client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reuse.status_code == 401
    # reuse detection: the stolen-token family is revoked too
    after = await client.post("/api/auth/refresh", json={"refresh_token": second["refresh_token"]})
    assert after.status_code == 401


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_to_refresh(ctx):
    client, _, _ = ctx
    tokens = (await _login(client)).json()
    r = await client.post("/api/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(ctx):
    client, _, _ = ctx
    tokens = (await _login(client)).json()
    out = await client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert out.status_code == 200
    r = await client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 401


# --- S-10: rate limiting -----------------------------------------------------

@pytest.mark.asyncio
async def test_login_locks_out_after_repeated_failures(ctx):
    client, _, _ = ctx
    for _ in range(settings.LOGIN_MAX_ATTEMPTS):
        assert (await _login(client, password="mala")).status_code == 401
    locked = await _login(client)  # even the right password is refused while locked
    assert locked.status_code == 429
    assert int(locked.headers["Retry-After"]) > 0


@pytest.mark.asyncio
async def test_successful_login_resets_failure_counter(ctx):
    client, _, _ = ctx
    for _ in range(settings.LOGIN_MAX_ATTEMPTS - 1):
        await _login(client, password="mala")
    assert (await _login(client)).status_code == 200
    for _ in range(settings.LOGIN_MAX_ATTEMPTS - 1):
        await _login(client, password="mala")
    assert (await _login(client)).status_code == 200


# --- S-05: public registration ----------------------------------------------

@pytest.mark.asyncio
async def test_public_register_disabled_by_default(ctx):
    client, _, _ = ctx
    r = await client.post("/api/auth/register", json={"email": "x@test.com", "password": "Segura123!"})
    assert r.status_code == 403
    cfg = await client.get("/api/auth/config")
    assert cfg.json() == {"public_register": False}


@pytest.mark.asyncio
async def test_public_register_when_enabled_creates_alumno(ctx, monkeypatch):
    client, factory, _ = ctx
    monkeypatch.setattr(settings, "ALLOW_PUBLIC_REGISTER", True)
    r = await client.post("/api/auth/register", json={"email": "nuevo@test.com", "password": "Segura123!"})
    assert r.status_code == 201
    async with factory() as s:
        roles = (await s.execute(
            select(Role.name).join(UserRole).join(User).where(User.email == "nuevo@test.com")
        )).scalars().all()
    assert roles == ["ALUMNO"]


@pytest.mark.asyncio
async def test_register_rejects_short_password(ctx, monkeypatch):
    client, _, _ = ctx
    monkeypatch.setattr(settings, "ALLOW_PUBLIC_REGISTER", True)
    r = await client.post("/api/auth/register", json={"email": "corta@test.com", "password": "123"})
    assert r.status_code == 422


# --- S-07: real 2FA ----------------------------------------------------------

@pytest.mark.asyncio
async def test_2fa_endpoints_require_authentication(ctx):
    client, _, _ = ctx
    assert (await client.post("/api/auth/2fa/enrol")).status_code == 401
    assert (await client.post("/api/auth/2fa/confirm", json={"code": "123456"})).status_code == 401


@pytest.mark.asyncio
async def test_2fa_full_flow(ctx):
    client, factory, user = ctx
    access = (await _login(client)).json()["access_token"]

    enrol = await client.post("/api/auth/2fa/enrol", headers=_bearer(access))
    assert enrol.status_code == 200
    secret = enrol.json()["secret"]
    assert "ana%40test.com" in enrol.json()["qr_code_uri"]

    async with factory() as s:
        stored = await s.get(User, user.id)
        assert stored.is_2fa_enabled is False  # not active until confirmed
        assert stored.totp_secret and stored.totp_secret != secret  # encrypted at rest

    bad = await client.post("/api/auth/2fa/confirm", json={"code": "000000"}, headers=_bearer(access))
    assert bad.status_code == 400
    ok = await client.post(
        "/api/auth/2fa/confirm", json={"code": pyotp.TOTP(secret).now()}, headers=_bearer(access)
    )
    assert ok.status_code == 200

    # login now requires the TOTP code
    missing = await _login(client)
    assert missing.status_code == 403
    assert missing.json()["detail"] == "totp_required"
    assert (await _login(client, totp_code="000000")).status_code == 401
    assert (await _login(client, totp_code=pyotp.TOTP(secret).now())).status_code == 200

    off = await client.post(
        "/api/auth/2fa/disable", json={"code": pyotp.TOTP(secret).now()}, headers=_bearer(access)
    )
    assert off.status_code == 200
    assert (await _login(client)).status_code == 200
