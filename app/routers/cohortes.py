import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_permission, get_current_user
from app.models.cohorte import Cohorte
from app.models.user import User
from app.repositories.carrera import CarreraRepository
from app.repositories.cohorte import CohorteRepository
from app.schemas.cohorte import CohorteCreate, CohorteRead, CohorteUpdate

router = APIRouter(prefix="/api/cohortes", tags=["cohortes"])
_gestionar = check_permission("estructura:gestionar")


async def _ensure_carrera_in_tenant(db: AsyncSession, carrera_id: uuid.UUID, user: User) -> None:
    if await CarreraRepository(db).get_in_tenant(carrera_id, user.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Carrera not found")


async def _get_or_404(repo: CohorteRepository, cohorte_id: uuid.UUID, user: User) -> Cohorte:
    cohorte = await repo.get_in_tenant(cohorte_id, user.tenant_id)
    if cohorte is None:
        raise HTTPException(status_code=404, detail="Cohorte not found")
    return cohorte


@router.get("", response_model=list[CohorteRead])
async def get_cohortes(
    carrera_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repo = CohorteRepository(db)
    if carrera_id:
        return await repo.get_by_carrera(user.tenant_id, carrera_id)
    return await repo.get_all(user.tenant_id)


@router.post("", response_model=CohorteRead)
async def create_cohorte(cohorte_in: CohorteCreate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    await _ensure_carrera_in_tenant(db, cohorte_in.carrera_id, user)
    return await CohorteRepository(db).create(Cohorte(**cohorte_in.model_dump(), tenant_id=user.tenant_id))


@router.put("/{cohorte_id}", response_model=CohorteRead)
async def update_cohorte(
    cohorte_id: uuid.UUID, body: CohorteUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)
):
    repo = CohorteRepository(db)
    cohorte = await _get_or_404(repo, cohorte_id, user)
    values = body.model_dump(exclude_unset=True)
    if values.get("carrera_id"):
        await _ensure_carrera_in_tenant(db, values["carrera_id"], user)
    return await repo.update(cohorte, values)


@router.delete("/{cohorte_id}")
async def delete_cohorte(cohorte_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    repo = CohorteRepository(db)
    await repo.soft_delete(await _get_or_404(repo, cohorte_id, user))
    return {"ok": True, "mensaje": "Cohorte eliminado"}
