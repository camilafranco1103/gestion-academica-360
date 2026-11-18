import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cohorte import Cohorte
from app.repositories.base import BaseRepository


class CohorteRepository(BaseRepository[Cohorte]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cohorte)

    async def create(self, cohorte: Cohorte) -> Cohorte:
        self.session.add(cohorte)
        await self.session.commit()
        await self.session.refresh(cohorte)
        return cohorte

    async def get_by_carrera(self, tenant_id: uuid.UUID, carrera_id: uuid.UUID) -> list[Cohorte]:
        stmt = self._scoped(tenant_id).where(Cohorte.carrera_id == carrera_id)
        return list((await self.session.execute(stmt)).scalars().all())
