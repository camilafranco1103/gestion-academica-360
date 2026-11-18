"""S-04 / S-11 / S-12 on usuarios and estructura académica.

Two tenants; the caller is ADMIN of tenant A with a real JWT and real
permissions. Anything belonging to tenant B must behave as non-existent (404).
"""
import uuid

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.auth import create_access_token
from app.core.database import get_db
from app.models.base import Base
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.rbac import Permission, Role, RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.routers.carreras import router as carreras_router
from app.routers.cohortes import router as cohortes_router
from app.routers.materias import router as materias_router
from app.routers.usuarios import router as usuarios_router
from app.routers.admin import router as admin_router


@pytest_asyncio.fixture
async def env():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    ids = {}
    async with factory() as s:
        ta, tb = Tenant(id=uuid.uuid4(), name="A"), Tenant(id=uuid.uuid4(), name="B")
        admin_role, profesor_role = Role(id=1, name="ADMIN"), Role(id=2, name="PROFESOR")
        p_users, p_estr = Permission(id=1, name="usuarios:gestionar"), Permission(id=2, name="estructura:gestionar")
        s.add_all([ta, tb, admin_role, profesor_role, p_users, p_estr])
        await s.flush()
        s.add_all([RolePermission(role_id=1, permission_id=1), RolePermission(role_id=1, permission_id=2)])

        admin = User(id=uuid.uuid4(), tenant_id=ta.id, email="admin@a.com", hashed_password="x")
        peer = User(id=uuid.uuid4(), tenant_id=ta.id, email="peer@a.com", hashed_password="x")
        victim = User(id=uuid.uuid4(), tenant_id=tb.id, email="victim@b.com", hashed_password="x")
        s.add_all([admin, peer, victim])
        await s.flush()
        s.add_all([UserRole(user_id=admin.id, role_id=1), UserRole(user_id=peer.id, role_id=2)])

        car_a = Carrera(id=uuid.uuid4(), tenant_id=ta.id, name="Car A", code="CA")
        car_b = Carrera(id=uuid.uuid4(), tenant_id=tb.id, name="Car B", code="CB")
        s.add_all([car_a, car_b])
        await s.flush()
        coh_b = Cohorte(id=uuid.uuid4(), tenant_id=tb.id, carrera_id=car_b.id, name="2026")
        mat_a = Materia(id=uuid.uuid4(), tenant_id=ta.id, name="Mat A", code="MA")
        mat_b = Materia(id=uuid.uuid4(), tenant_id=tb.id, name="Mat B", code="MB")
        s.add_all([coh_b, mat_a, mat_b])
        await s.commit()
        ids.update(admin=admin.id, peer=peer.id, victim=victim.id, car_a=car_a.id, car_b=car_b.id,
                   coh_b=coh_b.id, mat_a=mat_a.id, mat_b=mat_b.id, ta=ta.id)

    app = FastAPI()
    for r in (usuarios_router, carreras_router, cohortes_router, admin_router):
        app.include_router(r)
    app.include_router(materias_router, prefix="/api/materias")

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token({"sub": str(ids["admin"]), "tenant_id": str(ids["ta"])})
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers) as c:
        yield c, factory, ids
    await engine.dispose()


# --- usuarios ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_user_list_only_shows_own_tenant(env):
    c, _, _ = env
    emails = {u["email"] for u in (await c.get("/api/v1/usuarios?estado=todos")).json()}
    assert emails == {"admin@a.com", "peer@a.com"}


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", [
    ("GET", "/api/v1/usuarios/{victim}", None),
    ("PUT", "/api/v1/usuarios/{victim}", {"password": "Hijacked123!"}),
    ("PUT", "/api/v1/usuarios/{victim}/toggle-activo", None),
    ("POST", "/api/v1/usuarios/{victim}/roles", {"rol": "ADMIN"}),
    ("DELETE", "/api/v1/usuarios/{victim}/roles/1", None),
])
async def test_other_tenant_user_is_not_found(env, method, path, body):
    c, _, ids = env
    r = await c.request(method, path.format(victim=ids["victim"]), json=body)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_user_update_rejects_unknown_fields(env):
    c, _, ids = env
    r = await c.put(f"/api/v1/usuarios/{ids['peer']}", json={"tenant_id": str(uuid.uuid4())})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_removing_a_role_is_a_soft_delete(env):
    c, factory, ids = env
    assert (await c.delete(f"/api/v1/usuarios/{ids['peer']}/roles/2")).status_code == 200
    detail = (await c.get(f"/api/v1/usuarios/{ids['peer']}")).json()
    assert detail["roles"] == []
    async with factory() as s:
        link = (await s.execute(select(UserRole).where(UserRole.user_id == ids["peer"]))).scalar_one()
        assert link.deleted_at is not None
    # re-assigning reactivates the same link
    assert (await c.post(f"/api/v1/usuarios/{ids['peer']}/roles", json={"rol": "PROFESOR"})).status_code == 200
    assert [r["name"] for r in (await c.get(f"/api/v1/usuarios/{ids['peer']}")).json()["roles"]] == ["PROFESOR"]


@pytest.mark.asyncio
async def test_admin_create_user_lands_in_callers_tenant(env):
    c, factory, ids = env
    r = await c.post("/api/admin/usuarios/", json={"email": "new@a.com", "password": "Segura123!"})
    assert r.status_code == 200
    assert r.json()["tenant_id"] == str(ids["ta"])


# --- estructura académica ---------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", [
    ("GET", "/api/carreras/{car_b}", None),
    ("PUT", "/api/carreras/{car_b}", {"name": "pwned"}),
    ("DELETE", "/api/carreras/{car_b}", None),
    ("PUT", "/api/cohortes/{coh_b}", {"name": "pwned"}),
    ("DELETE", "/api/cohortes/{coh_b}", None),
    ("PUT", "/api/materias/{mat_b}", {"name": "pwned"}),
    ("DELETE", "/api/materias/{mat_b}", None),
])
async def test_other_tenant_structure_is_not_found(env, method, path, body):
    c, factory, ids = env
    r = await c.request(method, path.format(**ids), json=body)
    assert r.status_code == 404
    async with factory() as s:
        assert (await s.get(Materia, ids["mat_b"])).name == "Mat B"
        assert (await s.get(Carrera, ids["car_b"])).deleted_at is None


@pytest.mark.asyncio
async def test_cohorte_cannot_be_moved_to_other_tenants_carrera(env):
    c, _, ids = env
    r = await c.post("/api/cohortes", json={"name": "X", "carrera_id": str(ids["car_b"])})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_structure_updates_reject_unknown_fields(env):
    c, _, ids = env
    assert (await c.put(f"/api/materias/{ids['mat_a']}", json={"tenant_id": "x"})).status_code == 422
    assert (await c.put(f"/api/carreras/{ids['car_a']}", json={"tenant_id": "x"})).status_code == 422


@pytest.mark.asyncio
async def test_deleting_a_materia_is_a_soft_delete(env):
    c, factory, ids = env
    assert (await c.delete(f"/api/materias/{ids['mat_a']}")).status_code == 200
    listed = {m["id"] for m in (await c.get("/api/materias")).json()}
    assert str(ids["mat_a"]) not in listed
    async with factory() as s:
        assert (await s.get(Materia, ids["mat_a"])).deleted_at is not None


@pytest.mark.asyncio
async def test_deleting_a_carrera_is_a_soft_delete(env):
    c, factory, ids = env
    assert (await c.delete(f"/api/carreras/{ids['car_a']}")).status_code == 200
    assert (await c.get(f"/api/carreras/{ids['car_a']}")).status_code == 404
    assert str(ids["car_a"]) not in {x["id"] for x in (await c.get("/api/carreras")).json()}
    async with factory() as s:
        assert (await s.get(Carrera, ids["car_a"])).deleted_at is not None


# --- S-15: no privilege escalation through role assignment --------------------

@pytest.mark.asyncio
async def test_cannot_change_own_roles(env):
    c, _, ids = env
    r = await c.post(f"/api/v1/usuarios/{ids['admin']}/roles", json={"rol": "PROFESOR"})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_non_admin_with_user_permission_cannot_grant_admin(env):
    """Even if a non-ADMIN role were (mis)granted usuarios:gestionar, it can't mint ADMINs."""
    c, factory, ids = env
    async with factory() as s:
        coord = Role(id=3, name="COORDINADOR")
        s.add(coord)
        await s.flush()
        s.add(RolePermission(role_id=3, permission_id=1))  # usuarios:gestionar
        s.add(UserRole(user_id=ids["peer"], role_id=3))
        await s.commit()
    token = create_access_token({"sub": str(ids["peer"])})
    r = await c.post(
        f"/api/v1/usuarios/{ids['admin']}/roles",
        json={"rol": "ADMIN"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
