import uuid
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Tenant-scoped CRUD. Soft-deleted rows are invisible to every read."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    def _scoped(self, tenant_id: Any):
        stmt = select(self.model).where(self.model.tenant_id == tenant_id)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return stmt

    async def get_all(self, tenant_id: Any) -> list[T]:
        result = await self.session.execute(self._scoped(tenant_id))
        return list(result.scalars().all())

    async def get_in_tenant(self, obj_id: uuid.UUID, tenant_id: Any) -> T | None:
        stmt = self._scoped(tenant_id).where(self.model.id == obj_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def soft_delete(self, obj: T) -> None:
        obj.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.commit()

    async def update(self, obj: T, values: dict) -> T:
        for field, value in values.items():
            setattr(obj, field, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
