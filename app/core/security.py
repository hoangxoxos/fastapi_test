import hashlib
import secrets

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(payload: dict) -> str:
    return jwt.encode(payload, settings.access_key, algorithm=settings.algorithm)


def verify_access_token(token: str) -> dict:
    return jwt.decode(token, settings.access_key, algorithms=settings.algorithm)


def generate_random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
