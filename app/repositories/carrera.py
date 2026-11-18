from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.repositories.base import BaseRepository


class CarreraRepository(BaseRepository[Carrera]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Carrera)

    async def create(self, carrera: Carrera) -> Carrera:
        self.session.add(carrera)
        await self.session.commit()
        await self.session.refresh(carrera)
        return carrera
