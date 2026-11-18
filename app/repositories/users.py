"""User and refresh-token persistence. Every tenant-facing lookup is scoped."""
import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rbac import Role, RolePermission
from app.models.tenant import Tenant
from app.models.token import RefreshToken
from app.models.user import User
from app.models.user_role import UserRole


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _with_roles(stmt):
    return stmt.options(
        selectinload(User.user_roles)
        .selectinload(UserRole.role)
        .selectinload(Role.role_permissions)
        .selectinload(RolePermission.permission)
    )


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- authentication (global by email: emails are unique across tenants) ---

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email)
        return (await self.session.execute(stmt)).first() is not None

    async def get_with_permissions(self, user_id: uuid.UUID) -> User | None:
        stmt = _with_roles(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_default_tenant(self) -> Tenant | None:
        stmt = select(Tenant).order_by(Tenant.created_at).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # --- tenant-scoped administration ---

    async def get_in_tenant(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> User | None:
        stmt = _with_roles(
            select(User).where(User.id == user_id, User.tenant_id == tenant_id, User.deleted_at.is_(None))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_in_tenant(self, tenant_id: uuid.UUID, activo: bool | None) -> list[User]:
        stmt = _with_roles(select(User).where(User.tenant_id == tenant_id, User.deleted_at.is_(None)))
        if activo is not None:
            stmt = stmt.where(User.activo == activo)
        return list((await self.session.execute(stmt.order_by(User.email))).scalars().all())

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    # --- roles (global catalogue) ---

    async def list_roles(self) -> list[Role]:
        return list((await self.session.execute(select(Role).order_by(Role.name))).scalars().all())

    async def get_role_by_id(self, role_id: int) -> Role | None:
        return await self.session.get(Role, role_id)

    async def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name.upper())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_user_role(self, user_id: uuid.UUID, role_id: int) -> UserRole | None:
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_user_role(self, user_id: uuid.UUID, role_id: int) -> UserRole:
        """Create the link, or reactivate it if it was soft-deleted before."""
        user_role = await self.get_user_role(user_id, role_id)
        if user_role is None:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.session.add(user_role)
        else:
            user_role.deleted_at = None
        await self.session.flush()
        return user_role

    async def remove_user_role(self, user_role: UserRole) -> None:
        user_role.deleted_at = _now()
        await self.session.flush()


class RefreshTokenRepository:
    """Stores only a SHA-256 of each refresh token's ``jti``. Revocation is soft."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def hash_jti(jti: str) -> str:
        return hashlib.sha256(jti.encode()).hexdigest()

    async def add(self, user_id: uuid.UUID, jti: str) -> None:
        self.session.add(RefreshToken(user_id=user_id, token=self.hash_jti(jti)))
        await self.session.flush()

    async def get(self, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == self.hash_jti(jti))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.deleted_at = _now()
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.deleted_at.is_(None))
            .values(deleted_at=_now())
        )
        await self.session.flush()
