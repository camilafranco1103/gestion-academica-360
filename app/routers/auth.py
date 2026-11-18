from dataclasses import asdict

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.user import User
from app.services.auth import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)
    totp_code: str | None = Field(default=None, min_length=6, max_length=8)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=1)


class TotpCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=6, max_length=8)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("/config")
async def auth_config():
    """Public, non-sensitive flags the login screen needs."""
    return {"public_register": settings.ALLOW_PUBLIC_REGISTER}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService(db).register(data.email, data.password)
    return {"id": str(user.id), "email": user.email, "mensaje": "Usuario registrado exitosamente"}


@router.post("/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    pair = await AuthService(db).login(data.email, data.password, data.totp_code, _client_ip(request))
    return asdict(pair)


@router.post("/refresh")
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return asdict(await AuthService(db).refresh(data.refresh_token))


@router.post("/logout")
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await AuthService(db).logout(data.refresh_token)
    return {"message": "Sesión cerrada"}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    roles = [ur.role.name for ur in user.user_roles if ur.role]
    permissions = sorted({
        rp.permission.name
        for ur in user.user_roles if ur.role
        for rp in ur.role.role_permissions if rp.permission
    })
    return {
        "id": str(user.id),
        "email": user.email,
        "nombre": user.nombre or (user.email or "").split("@")[0].capitalize(),
        "roles": roles,
        "permissions": permissions,
        "is_2fa_enabled": user.is_2fa_enabled,
    }


@router.post("/2fa/enrol")
async def enrol_2fa(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await AuthService(db).enrol_2fa(user)


@router.post("/2fa/confirm")
async def confirm_2fa(
    data: TotpCodeRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    await AuthService(db).confirm_2fa(user, data.code)
    return {"message": "2FA activado"}


@router.post("/2fa/disable")
async def disable_2fa(
    data: TotpCodeRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    await AuthService(db).disable_2fa(user, data.code)
    return {"message": "2FA desactivado"}
