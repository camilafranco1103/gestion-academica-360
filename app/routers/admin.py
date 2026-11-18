from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_permission
from app.models.user import User
from app.schemas.usuario import UserCreate, UserRead
from app.services.usuarios import UsuariosService

router = APIRouter(prefix="/api/admin/usuarios", tags=["admin"])


@router.post("/", response_model=UserRead)
async def create_usuario(
    usuario: UserCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(check_permission("usuarios:gestionar")),
):
    """Legacy endpoint: creates a user without a default role, in the caller's tenant."""
    return await UsuariosService(db, user).create(usuario, default_role=None)
