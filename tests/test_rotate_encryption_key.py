import uuid

import pytest
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import decrypt, encrypt
from app.db.rotate_encryption_key import _legacy_dev_key, rotate
from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
async def test_rotation_moves_legacy_values_to_current_key_and_is_idempotent():
    legacy = _legacy_dev_key()
    user_id = uuid.uuid4()
    async with AsyncSessionLocal() as s:
        tenant = Tenant(id=uuid.uuid4(), name=f"rot-{user_id.hex[:6]}")
        s.add(tenant)
        await s.flush()
        s.add(User(id=user_id, tenant_id=tenant.id, email=f"{user_id.hex}@rot.test", hashed_password="x"))
        await s.flush()
        await s.execute(
            text("UPDATE users SET dni = :d, totp_secret = :t WHERE id = :id"),
            {"d": encrypt("30111222", legacy), "t": "PLAINTOTPSECRET", "id": user_id.hex},
        )
        await s.commit()

    await rotate(legacy)
    await rotate(legacy)  # second run must not double-encrypt

    async with AsyncSessionLocal() as s:
        dni, totp = (await s.execute(
            text("SELECT dni, totp_secret FROM users WHERE id = :id"), {"id": user_id.hex}
        )).one()
    assert decrypt(dni, settings.encryption_key_bytes) == "30111222"
    assert decrypt(totp, settings.encryption_key_bytes) == "PLAINTOTPSECRET"
