import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_permission
from app.models.carrera import Carrera
from app.models.user import User
from app.repositories.carrera import CarreraRepository
from app.schemas.carrera import CarreraCreate, CarreraRead, CarreraUpdate

router = APIRouter(prefix="/api/carreras", tags=["carreras"])
_gestionar = check_permission("estructura:gestionar")


async def _get_or_404(repo: CarreraRepository, carrera_id: uuid.UUID, user: User) -> Carrera:
    carrera = await repo.get_in_tenant(carrera_id, user.tenant_id)
    if carrera is None:
        raise HTTPException(status_code=404, detail="Carrera not found")
    return carrera


@router.post("", response_model=CarreraRead)
async def create_carrera(carrera_in: CarreraCreate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    return await CarreraRepository(db).create(Carrera(**carrera_in.model_dump(), tenant_id=user.tenant_id))


@router.get("/{carrera_id}", response_model=CarreraRead)
async def get_carrera(carrera_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    return await _get_or_404(CarreraRepository(db), carrera_id, user)


@router.get("", response_model=list[CarreraRead])
async def get_carreras(db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    return await CarreraRepository(db).get_all(user.tenant_id)


@router.put("/{carrera_id}", response_model=CarreraRead)
async def update_carrera(
    carrera_id: uuid.UUID, body: CarreraUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)
):
    repo = CarreraRepository(db)
    carrera = await _get_or_404(repo, carrera_id, user)
    return await repo.update(carrera, body.model_dump(exclude_unset=True))


@router.delete("/{carrera_id}")
async def delete_carrera(carrera_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    repo = CarreraRepository(db)
    await repo.soft_delete(await _get_or_404(repo, carrera_id, user))
    return {"ok": True, "mensaje": "Carrera eliminada"}
