"""Authentication use cases: login, refresh rotation, logout, registration, 2FA."""
import uuid
from dataclasses import dataclass

import bcrypt
import pyotp
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.core.rate_limit import login_rate_limiter
from app.core.security import decrypt, encrypt
from app.models.user import User
from app.repositories.users import RefreshTokenRepository, UserRepository

TOTP_ISSUER = "Gestión Académica 360"


# --- TOTP primitives (kept as plain functions; used by tests and the service) ---

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def generate_totp_token(secret: str) -> str:
    return pyotp.TOTP(secret).now()


def verify_totp_token(secret: str, token: str) -> bool:
    if not secret or not token:
        return False
    return pyotp.TOTP(secret).verify(token, valid_window=1)


# --- helpers ---

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def _password_matches(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# Constant-time-ish dummy check so unknown emails cost the same as wrong passwords.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


def _unauthorized(detail: str = "Credenciales inválidas") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)

    async def _issue_tokens(self, user: User) -> TokenPair:
        claims = {"sub": str(user.id), "tenant_id": str(user.tenant_id)}
        jti = uuid.uuid4().hex
        await self.tokens.add(user.id, jti)
        return TokenPair(
            access_token=create_access_token(claims),
            refresh_token=create_refresh_token(claims, jti=jti),
        )

    # --- login ---

    async def login(self, email: str, password: str, totp_code: str | None, client_ip: str) -> TokenPair:
        retry_after = login_rate_limiter.retry_after(client_ip, email)
        if retry_after:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Probá de nuevo más tarde.",
                headers={"Retry-After": str(retry_after)},
            )

        user = await self.users.get_by_email(email)
        if user is None:
            _password_matches(password, _DUMMY_HASH)
            login_rate_limiter.register_failure(client_ip, email)
            raise _unauthorized()
        if not _password_matches(password, user.hashed_password) or not user.activo:
            login_rate_limiter.register_failure(client_ip, email)
            raise _unauthorized()

        if user.is_2fa_enabled:
            if not totp_code:
                # Password was right; the client must ask for the second factor.
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="totp_required")
            if not verify_totp_token(self._totp_secret(user), totp_code):
                login_rate_limiter.register_failure(client_ip, email)
                raise _unauthorized("Código de verificación inválido")

        login_rate_limiter.register_success(client_ip, email)
        pair = await self._issue_tokens(user)
        await self.db.commit()
        return pair

    # --- refresh rotation with reuse detection ---

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = verify_token(refresh_token, expected_type="refresh")
        if not payload or not payload.get("jti"):
            raise _unauthorized("Refresh token inválido")

        stored = await self.tokens.get(payload["jti"])
        if stored is None:
            raise _unauthorized("Refresh token inválido")
        if stored.deleted_at is not None:
            # A revoked token is being replayed: assume theft, end every session.
            await self.tokens.revoke_all_for_user(stored.user_id)
            await self.db.commit()
            raise _unauthorized("Refresh token revocado")

        user = await self.users.get_with_permissions(stored.user_id)
        if user is None or not user.activo or str(user.id) != payload.get("sub"):
            raise _unauthorized("Refresh token inválido")

        await self.tokens.revoke(stored)
        pair = await self._issue_tokens(user)
        await self.db.commit()
        return pair

    async def logout(self, refresh_token: str) -> None:
        payload = verify_token(refresh_token, expected_type="refresh")
        if payload and payload.get("jti"):
            stored = await self.tokens.get(payload["jti"])
            if stored is not None and stored.deleted_at is None:
                await self.tokens.revoke(stored)
                await self.db.commit()

    # --- public registration (S-05) ---

    async def register(self, email: str, password: str) -> User:
        if not settings.ALLOW_PUBLIC_REGISTER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registro público deshabilitado")
        if await self.users.email_exists(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")

        # Single-institution deployments only: self-registration joins the
        # first tenant. Multi-tenant deployments keep registration disabled.
        tenant = await self.users.get_default_tenant()
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No hay institución configurada")

        user = await self.users.add(User(tenant_id=tenant.id, email=email, hashed_password=hash_password(password)))
        alumno = await self.users.get_role_by_name("ALUMNO")
        if alumno:
            await self.users.add_user_role(user.id, alumno.id)
        await self.db.commit()
        return user

    # --- 2FA (S-07) ---

    @staticmethod
    def _totp_secret(user: User) -> str | None:
        return decrypt(user.totp_secret) if user.totp_secret else None

    async def enrol_2fa(self, user: User) -> dict:
        if user.is_2fa_enabled:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="2FA ya está activo")
        secret = generate_totp_secret()
        user.totp_secret = encrypt(secret)
        await self.db.commit()
        uri = pyotp.TOTP(secret).provisioning_uri(user.email or str(user.id), issuer_name=TOTP_ISSUER)
        return {"secret": secret, "qr_code_uri": uri}

    async def confirm_2fa(self, user: User, code: str) -> None:
        if not verify_totp_token(self._totp_secret(user), code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido")
        user.is_2fa_enabled = True
        await self.db.commit()

    async def disable_2fa(self, user: User, code: str) -> None:
        if not user.is_2fa_enabled or not verify_totp_token(self._totp_secret(user), code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido")
        user.is_2fa_enabled = False
        user.totp_secret = None
        await self.db.commit()
