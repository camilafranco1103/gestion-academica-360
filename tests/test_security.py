import pytest

from app.core.security import decrypt, encrypt

KEY = b"0123456789abcdef0123456789abcdef"  # 32 bytes for AES-256


def test_encryption_decryption():
    encrypted = encrypt("sensitive-pii-data", KEY)
    assert encrypted != "sensitive-pii-data"
    assert decrypt(encrypted, KEY) == "sensitive-pii-data"


def test_encryption_decryption_long_string():
    data = "a" * 1000
    assert decrypt(encrypt(data, KEY), KEY) == data


def test_encryption_decryption_special_chars():
    data = "!@#$%^&*()_+{}|:<>?1234567890-=[]\\;',./"
    assert decrypt(encrypt(data, KEY), KEY) == data


def test_default_key_comes_from_settings():
    assert decrypt(encrypt("dni-123")) == "dni-123"


@pytest.mark.parametrize("bad_key", [b"short", b"x" * 31, b"x" * 33, "a-string-key-of-32-characters!!!"])
def test_keys_that_are_not_32_bytes_are_rejected(bad_key):
    """S-08: no zero-padding or truncation of weak keys."""
    with pytest.raises(ValueError):
        encrypt("data", bad_key)


def test_wrong_key_cannot_decrypt():
    token = encrypt("secreto", KEY)
    with pytest.raises(Exception):
        decrypt(token, b"z" * 32)
