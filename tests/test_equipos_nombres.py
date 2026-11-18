"""The equipos listing carries readable names so the UI never shows raw IDs."""
import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.auth import create_access_token
from app.core.database import get_db
from app.models.asignacion import Asignacion
from app.models.base import Base
from app.models.materia import Materia
from app.models.rbac import Permission, Role, RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.routers.equipos import router as equipos_router


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        t = Tenant(id=uuid.uuid4(), name="T")
        coord, prof = Role(id=1, name="COORDINADOR"), Role(id=2, name="PROFESOR")
        perm = Permission(id=1, name="equipos:asignar")
        s.add_all([t, coord, prof, perm])
        await s.flush()
        s.add(RolePermission(role_id=1, permission_id=1))
        actor = User(id=uuid.uuid4(), tenant_id=t.id, email="c@t.com", hashed_password="x")
        docente = User(id=uuid.uuid4(), tenant_id=t.id, email="ana@t.com", nombre="Ana Pérez", hashed_password="x")
        materia = Materia(id=uuid.uuid4(), tenant_id=t.id, name="Álgebra", code="ALG")
        s.add_all([actor, docente, materia])
        await s.flush()
        s.add(UserRole(user_id=actor.id, role_id=1))
        s.add(Asignacion(tenant_id=t.id, user_id=docente.id, role_id=2, contexto_id=materia.id, desde=datetime(2026, 3, 1)))
        await s.commit()
        actor_id = actor.id

    app = FastAPI()
    app.include_router(equipos_router)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {create_access_token({'sub': str(actor_id)})}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers) as c:
        yield c
    await engine.dispose()


@pytest.mark.asyncio
async def test_listado_incluye_nombres(client):
    r = await client.get("/api/equipos")
    assert r.status_code == 200
    [row] = r.json()
    assert row["docente_nombre"] == "Ana Pérez"
    assert row["rol_nombre"] == "PROFESOR"
    assert row["contexto_nombre"] == "Álgebra"
