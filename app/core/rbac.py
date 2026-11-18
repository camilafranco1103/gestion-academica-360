import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_token
from app.core.database import get_db
from app.models.user import User
from app.repositories.users import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Identity comes ONLY from a verified access token (rule 8)."""
    payload = verify_token(token, expected_type="access")
    if not payload:
        raise _unauthorized("Could not validate credentials")
    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise _unauthorized("Invalid user ID format")

    user = await UserRepository(db).get_with_permissions(user_id)
    if user is None or not user.activo:
        raise _unauthorized("User not found")
    return user


def user_has_permission(user: User, permission_name: str) -> bool:
    return any(
        rp.permission is not None and rp.permission.name == permission_name
        for ur in user.user_roles if ur.role is not None
        for rp in ur.role.role_permissions
    )


def check_permission(permission_name: str):
    """Fail-closed RBAC guard: the user must hold ``permission_name`` via an active role."""
    async def _check_permission(user: User = Depends(get_current_user)) -> User:
        if user_has_permission(user, permission_name):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso requerido: {permission_name}",
        )
    return _check_permission
