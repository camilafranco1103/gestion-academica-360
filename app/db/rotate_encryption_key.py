"""Re-encrypt every AES-256 column from an old key to the current ENCRYPTION_KEY.

Usage:
    # old key given as urlsafe base64 of 32 bytes
    OLD_ENCRYPTION_KEY=<base64> python -m app.db.rotate_encryption_key
    # data written before S-08 with the insecure default "dev-key"
    python -m app.db.rotate_encryption_key --from-legacy-dev-key

Runs in a single transaction: either every value is rotated or nothing is.
Values that already decrypt with the new key are left untouched, so the
script is safe to re-run.
"""
import argparse
import asyncio
import base64
import os
import sys

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.security import decrypt, encrypt

# (table, primary key column, encrypted column)
ENCRYPTED_COLUMNS = [
    ("users", "id", "dni"),
    ("users", "id", "cuil"),
    ("users", "id", "cbu"),
    ("users", "id", "totp_secret"),
    ("comunicaciones", "id", "destinatario"),
    ("entradas_padron", "id", "email"),
]


def _legacy_dev_key() -> bytes:
    # Reproduces the pre-S-08 derivation: "dev-key" right-padded with NULs.
    return b"dev-key".ljust(32, b"\0")


def _old_key(args: argparse.Namespace) -> bytes:
    if args.from_legacy_dev_key:
        return _legacy_dev_key()
    raw = os.environ.get("OLD_ENCRYPTION_KEY")
    if not raw:
        sys.exit("Definí OLD_ENCRYPTION_KEY o usá --from-legacy-dev-key")
    key = base64.urlsafe_b64decode(raw.encode())
    if len(key) != 32:
        sys.exit("OLD_ENCRYPTION_KEY debe decodificar a 32 bytes")
    return key


def _rotate_value(value: str, old: bytes, new: bytes) -> str | None:
    """Return the re-encrypted value, or None when no change is needed."""
    try:
        decrypt(value, new)
        return None  # already on the new key
    except Exception:
        pass
    try:
        # totp_secret was stored in plain text before S-07; encrypt it as-is.
        plain = decrypt(value, old)
    except Exception:
        plain = value
    return encrypt(plain, new)


async def rotate(old: bytes) -> dict[str, int]:
    new = settings.encryption_key_bytes
    counts: dict[str, int] = {}
    async with engine.begin() as conn:
        for table, pk, column in ENCRYPTED_COLUMNS:
            rows = (await conn.execute(text(f"SELECT {pk}, {column} FROM {table} WHERE {column} IS NOT NULL"))).all()
            changed = 0
            for row_id, value in rows:
                rotated = _rotate_value(value, old, new)
                if rotated is not None:
                    await conn.execute(
                        text(f"UPDATE {table} SET {column} = :v WHERE {pk} = :id"), {"v": rotated, "id": row_id}
                    )
                    changed += 1
            counts[f"{table}.{column}"] = changed
    await engine.dispose()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-legacy-dev-key", action="store_true")
    args = parser.parse_args()
    for column, changed in asyncio.run(rotate(_old_key(args))).items():
        print(f"{column}: {changed} valores re-cifrados")


if __name__ == "__main__":
    main()
