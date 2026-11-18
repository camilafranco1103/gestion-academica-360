"""User administration inside the caller's tenant (S-04)."""
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.usuario import UserCreate, UserUpdate
from app.services.auth import hash_password

_ESTADOS = {"activos": True, "inactivos": False, "todos": None}


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


def _role_names(user: User) -> list[str]:
    return [ur.role.name for ur in user.user_roles if ur.role]


class UsuariosService:
    def __init__(self, db: AsyncSession, actor: User):
        self.db = db
        self.actor = actor
        self.repo = UserRepository(db)

    async def _get(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_in_tenant(user_id, self.actor.tenant_id)
        if user is None:
            raise _not_found()
        return user

    async def list_roles(self) -> list[dict]:
        return [{"id": r.id, "name": r.name} for r in await self.repo.list_roles()]

    async def list_users(self, estado: str) -> list[dict]:
        if estado not in _ESTADOS:
            raise HTTPException(status_code=422, detail="estado debe ser activos, inactivos o todos")
        users = await self.repo.list_in_tenant(self.actor.tenant_id, _ESTADOS[estado])
        return [
            {
                "id": str(u.id),
                "nombre": u.nombre or (u.email or "").split("@")[0],
                "email": u.email,
                "roles": _role_names(u),
                "activo": u.activo,
            }
            for u in users
        ]

    async def detail(self, user_id: uuid.UUID) -> dict:
        user = await self._get(user_id)
        return {
            "id": str(user.id),
            "email": user.email,
            "nombre": user.nombre,
            "dni": user.dni,
            "cuil": user.cuil,
            "cbu": user.cbu,
            "datos_fiscales": user.datos_fiscales,
            "datos_bancarios": user.datos_bancarios,
            "regional": user.regional,
            "modalidad_cobro": user.modalidad_cobro,
            "activo": user.activo,
            "roles": [{"id": ur.role.id, "name": ur.role.name} for ur in user.user_roles if ur.role],
        }

    async def create(self, body: UserCreate, default_role: str | None = "ALUMNO") -> User:
        if await self.repo.email_exists(body.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")

        if body.role_id is not None:
            role = await self.repo.get_role_by_id(body.role_id)
            if role is None:
                raise HTTPException(status_code=404, detail=f"Rol id={body.role_id} no encontrado")
            if role.name == "ADMIN" and "ADMIN" not in _role_names(self.actor):
                raise HTTPException(status_code=403, detail="Solo un ADMIN puede otorgar el rol ADMIN")
        else:
            role = await self.repo.get_role_by_name(default_role) if default_role else None

        data = body.model_dump(exclude={"password", "role_id"})
        user = await self.repo.add(
            User(tenant_id=self.actor.tenant_id, hashed_password=hash_password(body.password), **data)
        )
        if role is not None:
            await self.repo.add_user_role(user.id, role.id)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: uuid.UUID, body: UserUpdate) -> None:
        user = await self._get(user_id)
        values = body.model_dump(exclude_unset=True)
        if "email" in values and values["email"] != user.email and await self.repo.email_exists(values["email"]):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")
        password = values.pop("password", None)
        for field, value in values.items():
            setattr(user, field, value)
        if password:
            user.hashed_password = hash_password(password)
        await self.db.commit()

    async def toggle_activo(self, user_id: uuid.UUID) -> bool:
        user = await self._get(user_id)
        if user.id == self.actor.id:
            raise HTTPException(status_code=400, detail="No podés desactivar tu propio usuario")
        user.activo = not user.activo
        await self.db.commit()
        return user.activo

    def _guard_role_change(self, user: User, role_name: str) -> None:
        """S-15: no self-service role changes and only ADMINs can mint ADMINs."""
        if user.id == self.actor.id:
            raise HTTPException(status_code=400, detail="No podés modificar tus propios roles")
        if role_name == "ADMIN" and "ADMIN" not in _role_names(self.actor):
            raise HTTPException(status_code=403, detail="Solo un ADMIN puede otorgar o quitar el rol ADMIN")

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> str:
        role = await self.repo.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=404, detail=f"Rol '{role_name}' no encontrado")
        user = await self._get(user_id)
        self._guard_role_change(user, role.name)
        if role.name in _role_names(user):
            return f"El usuario ya tiene el rol '{role.name}'"
        await self.repo.add_user_role(user.id, role.id)
        await self.db.commit()
        return f"Rol '{role.name}' asignado correctamente"

    async def remove_role(self, user_id: uuid.UUID, role_id: int) -> None:
        user = await self._get(user_id)
        link = await self.repo.get_user_role(user.id, role_id)
        if link is None or link.deleted_at is not None:
            raise HTTPException(status_code=404, detail="El usuario no tiene ese rol asignado")
        role = await self.repo.get_role_by_id(role_id)
        self._guard_role_change(user, role.name if role else "")
        await self.repo.remove_user_role(link)
        await self.db.commit()
