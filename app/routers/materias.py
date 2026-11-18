import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_permission, get_current_user
from app.models.materia import Materia
from app.models.user import User
from app.repositories.materia import MateriaRepository
from app.schemas.materia import MateriaCreate, MateriaRead, MateriaUpdate

router = APIRouter(tags=["materias"])
_gestionar = check_permission("estructura:gestionar")


async def _get_or_404(repo: MateriaRepository, materia_id: uuid.UUID, user: User) -> Materia:
    materia = await repo.get_in_tenant(materia_id, user.tenant_id)
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    return materia


@router.get("", response_model=list[MateriaRead])
async def get_materias(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await MateriaRepository(db).get_all(user.tenant_id)


@router.post("", response_model=MateriaRead)
async def create_materia(materia_in: MateriaCreate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    return await MateriaRepository(db).create(Materia(**materia_in.model_dump(), tenant_id=user.tenant_id))


@router.put("/{materia_id}", response_model=MateriaRead)
async def update_materia(
    materia_id: uuid.UUID, body: MateriaUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)
):
    repo = MateriaRepository(db)
    materia = await _get_or_404(repo, materia_id, user)
    return await repo.update(materia, body.model_dump(exclude_unset=True))


@router.delete("/{materia_id}")
async def delete_materia(materia_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(_gestionar)):
    repo = MateriaRepository(db)
    await repo.soft_delete(await _get_or_404(repo, materia_id, user))
    return {"ok": True, "mensaje": "Materia eliminada"}
