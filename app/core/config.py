import base64
import binascii

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # Secrets: required, no defaults. The app refuses to start without them.
    JWT_SECRET: str
    ENCRYPTION_KEY: str  # urlsafe base64 of exactly 32 bytes (AES-256)

    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7

    ALLOW_PUBLIC_REGISTER: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"
    SQL_ECHO: bool = False

    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("JWT_SECRET")
    @classmethod
    def _jwt_secret_strength(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET debe tener al menos 32 caracteres")
        return value

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def _encryption_key_size(cls, value: str) -> str:
        try:
            raw = base64.urlsafe_b64decode(value.encode())
        except (binascii.Error, ValueError) as exc:
            raise ValueError("ENCRYPTION_KEY debe ser base64") from exc
        if len(raw) != 32:
            raise ValueError("ENCRYPTION_KEY debe decodificar a 32 bytes (AES-256)")
        return value

    @property
    def encryption_key_bytes(self) -> bytes:
        return base64.urlsafe_b64decode(self.ENCRYPTION_KEY.encode())

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
