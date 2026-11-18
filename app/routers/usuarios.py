import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_permission
from app.models.user import User
from app.schemas.usuario import AsignarRolRequest, UserCreate, UserRead, UserUpdate
from app.services.usuarios import UsuariosService

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])
_gestionar = check_permission("usuarios:gestionar")


def _service(db: AsyncSession = Depends(get_db), actor: User = Depends(_gestionar)) -> UsuariosService:
    return UsuariosService(db, actor)


@router.get("/roles")
async def listar_roles(svc: UsuariosService = Depends(_service)):
    return await svc.list_roles()


@router.get("")
async def listar_usuarios(estado: str = "activos", svc: UsuariosService = Depends(_service)):
    return await svc.list_users(estado)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario_admin(body: UserCreate, svc: UsuariosService = Depends(_service)):
    return await svc.create(body)


@router.get("/{user_id}")
async def obtener_usuario(user_id: uuid.UUID, svc: UsuariosService = Depends(_service)):
    return await svc.detail(user_id)


@router.put("/{user_id}")
async def actualizar_usuario(user_id: uuid.UUID, body: UserUpdate, svc: UsuariosService = Depends(_service)):
    await svc.update(user_id, body)
    return {"ok": True, "mensaje": "Usuario actualizado correctamente"}


@router.put("/{user_id}/toggle-activo")
async def toggle_activo(user_id: uuid.UUID, svc: UsuariosService = Depends(_service)):
    activo = await svc.toggle_activo(user_id)
    estado = "activado" if activo else "desactivado"
    return {"ok": True, "activo": activo, "mensaje": f"Usuario {estado} correctamente"}


@router.post("/{user_id}/roles")
async def asignar_rol(user_id: uuid.UUID, body: AsignarRolRequest, svc: UsuariosService = Depends(_service)):
    return {"ok": True, "mensaje": await svc.assign_role(user_id, body.rol)}


@router.delete("/{user_id}/roles/{role_id}")
async def remover_rol(user_id: uuid.UUID, role_id: int, svc: UsuariosService = Depends(_service)):
    await svc.remove_role(user_id, role_id)
    return {"ok": True, "mensaje": "Rol removido correctamente"}
