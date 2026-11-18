"""S-15: the RBAC seed mirrors the KB matrix and revokes stale grants."""
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool

from app.db.seed import PERMISSIONS, ROLES, sync_rbac
from app.models.base import Base
from app.models.rbac import Permission, Role, RolePermission


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as s:
        yield s
    await engine.dispose()


async def _grants(s) -> dict[str, set[str]]:
    roles = (await s.execute(
        select(Role).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )).scalars().all()
    out: dict[str, set[str]] = {}
    for r in roles:
        for rp in r.role_permissions:
            out.setdefault(rp.permission.name, set()).add(r.name)
    return out


def test_only_admin_manages_users_and_structure():
    assert PERMISSIONS["usuarios:gestionar"] == ["ADMIN"]
    assert PERMISSIONS["estructura:gestionar"] == ["ADMIN"]
    assert set(PERMISSIONS["equipos:asignar"]) == {"COORDINADOR", "ADMIN"}


def test_every_permission_required_by_a_router_is_seeded():
    import pathlib
    import re

    required = set()
    for f in pathlib.Path("app/routers").glob("*.py"):
        required |= set(re.findall(r'check_permission\("([a-z_]+:[a-z_-]+)"\)', f.read_text(encoding="utf-8")))
    assert required - set(PERMISSIONS) == set()


@pytest.mark.asyncio
async def test_sync_creates_matrix_and_revokes_stale_grants(session):
    await sync_rbac(session)
    # simulate an old, over-permissive grant: COORDINADOR with usuarios:gestionar
    coord = (await session.execute(select(Role).where(Role.name == "COORDINADOR"))).scalar_one()
    perm = (await session.execute(select(Permission).where(Permission.name == "usuarios:gestionar"))).scalar_one()
    session.add(RolePermission(role_id=coord.id, permission_id=perm.id))
    await session.commit()
    assert "COORDINADOR" in (await _grants(session))["usuarios:gestionar"]

    await sync_rbac(session)
    session.expire_all()
    grants = await _grants(session)
    assert grants["usuarios:gestionar"] == {"ADMIN"}
    for name, roles in PERMISSIONS.items():
        assert grants.get(name, set()) == set(roles), name
    assert {r.name for r in (await session.execute(select(Role))).scalars()} == set(ROLES)

    # the stale link is soft-deleted, not removed
    link = (await session.execute(
        select(RolePermission).where(RolePermission.role_id == coord.id, RolePermission.permission_id == perm.id)
    )).scalar_one()
    assert link.deleted_at is not None
