"""RBAC catalogue: roles and the role × permission matrix.

The matrix mirrors knowledge-base/03_actores_y_roles.md §3. ``sync_rbac`` makes
the database match it exactly: missing grants are added (or reactivated) and
grants that are no longer in the matrix are soft-revoked. Safe to re-run.

Run: python -m app.db.seed
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.rbac import Permission, Role, RolePermission

ROLES = ["ALUMNO", "TUTOR", "PROFESOR", "COORDINADOR", "NEXO", "ADMIN", "FINANZAS"]

DOCENTES = ["TUTOR", "PROFESOR", "COORDINADOR", "ADMIN"]
COORDINACION = ["COORDINADOR", "ADMIN"]

PERMISSIONS: dict[str, list[str]] = {
    # académico
    "calificaciones:ver": DOCENTES,
    "calificaciones:importar": ["PROFESOR", "COORDINADOR", "ADMIN"],
    "calificaciones:vaciar": COORDINACION,
    "padron:ver": DOCENTES,
    "padron:importar": ["PROFESOR", "COORDINADOR", "ADMIN"],
    "padron:sincronizar": COORDINACION,
    "padron:vaciar": COORDINACION,
    # FINANZAS on atrasados:ver / comunicacion:enviar comes from commit aeaca56;
    # the KB matrix does not list it. Kept as-is pending a product decision.
    "atrasados:ver": ["PROFESOR", "TUTOR", "COORDINADOR", "ADMIN", "FINANZAS"],
    "atrasados:export": ["PROFESOR", "COORDINADOR", "ADMIN"],
    "comunicacion:enviar": ["PROFESOR", "COORDINADOR", "ADMIN", "FINANZAS"],
    "comunicacion:aprobar": COORDINACION,
    "encuentros:gestionar": ["PROFESOR", "COORDINADOR", "ADMIN"],
    "encuentros:ver": COORDINACION,
    "guardias:registrar": ["TUTOR", "COORDINADOR", "ADMIN"],
    "guardias:ver": COORDINACION,
    "coloquios:gestionar": COORDINACION,
    "coloquios:reservar": ["ALUMNO"],
    "coloquios:ver": ["COORDINADOR", "ADMIN", "PROFESOR", "ALUMNO"],
    "avisos:publicar": COORDINACION,
    "avisos:ver": ["ALUMNO", "TUTOR", "PROFESOR", "COORDINADOR", "NEXO", "ADMIN", "FINANZAS"],
    "avisos:confirmar": ["ALUMNO", "TUTOR", "PROFESOR", "COORDINADOR", "ADMIN", "FINANZAS"],
    "tareas:crear": ["PROFESOR", "COORDINADOR"],
    "tareas:ver": ["TUTOR", "PROFESOR", "COORDINADOR"],
    "tareas:gestionar": COORDINACION,
    # gestión (KB: equipos → COORDINADOR/ADMIN; estructura y usuarios → solo ADMIN)
    "equipos:asignar": COORDINACION,
    "estructura:gestionar": ["ADMIN"],
    "usuarios:gestionar": ["ADMIN"],
    "auditoria:ver": ["ADMIN", "COORDINADOR", "FINANZAS"],
    # finanzas
    "liquidaciones:ver": ["FINANZAS", "ADMIN"],
    "liquidaciones:configurar-salarios": ["FINANZAS"],
    "liquidaciones:cerrar": ["FINANZAS"],
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def sync_rbac(session: AsyncSession, verbose: bool = False) -> None:
    log = print if verbose else (lambda *_: None)

    roles: dict[str, Role] = {r.name: r for r in (await session.execute(select(Role))).scalars()}
    for name in ROLES:
        if name not in roles:
            roles[name] = Role(name=name)
            session.add(roles[name])
            log(f"+ rol {name}")
    await session.flush()

    perms: dict[str, Permission] = {p.name: p for p in (await session.execute(select(Permission))).scalars()}
    for name in PERMISSIONS:
        if name not in perms:
            perms[name] = Permission(name=name)
            session.add(perms[name])
            log(f"+ permiso {name}")
    await session.flush()

    wanted = {(roles[r].id, perms[p].id) for p, rs in PERMISSIONS.items() for r in rs}
    existing = {(rp.role_id, rp.permission_id): rp for rp in (await session.execute(select(RolePermission))).scalars()}

    for key in wanted:
        link = existing.get(key)
        if link is None:
            session.add(RolePermission(role_id=key[0], permission_id=key[1]))
        elif link.deleted_at is not None:
            link.deleted_at = None
    for key, link in existing.items():
        if key not in wanted and link.deleted_at is None:
            link.deleted_at = _now()  # soft revoke (S-11)
            log(f"- revocado role_id={key[0]} permission_id={key[1]}")
    await session.commit()


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        await sync_rbac(session, verbose=True)


if __name__ == "__main__":
    asyncio.run(seed())
