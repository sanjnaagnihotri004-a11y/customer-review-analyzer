"""
tests/test_auth.py
──────────────────
Unit tests for password hashing and authentication security.
"""

from services.auth import hash_password, verify_password


def test_hash_password_scrambles_plaintext():
    plain = "SuperSecretPass123"
    hashed = hash_password(plain)

    # The hashed output must NEVER equal the plaintext password
    assert hashed != plain
    # Standard bcrypt hashes begin with '$2b$'
    assert hashed.startswith("$2b$")


def test_hash_password_unique_salts():
    # Two identical passwords must produce different hashes because of unique random salts
    plain = "my_secure_password"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)

    assert hash1 != hash2


def test_verify_password_correct():
    plain = "correct_password"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_incorrect():
    plain = "correct_password"
    hashed = hash_password(plain)

    assert verify_password("wrong_password", hashed) is False
