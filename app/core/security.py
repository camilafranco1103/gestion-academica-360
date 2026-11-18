"""AES-256-GCM helpers for PII and secrets at rest.

The key always comes from ``settings.ENCRYPTION_KEY`` (32 raw bytes). Passing an
explicit key is only for key rotation and tests; it must also be 32 bytes.
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_SIZE = 12


def _resolve_key(key: bytes | None) -> bytes:
    if key is None:
        from app.core.config import settings

        key = settings.encryption_key_bytes
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("La clave AES-256 debe tener exactamente 32 bytes")
    return key


def encrypt(data: str, key: bytes | None = None) -> str:
    aesgcm = AESGCM(_resolve_key(key))
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt(token: str, key: bytes | None = None) -> str:
    aesgcm = AESGCM(_resolve_key(key))
    token_bytes = base64.b64decode(token)
    nonce, ciphertext = token_bytes[:_NONCE_SIZE], token_bytes[_NONCE_SIZE:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
