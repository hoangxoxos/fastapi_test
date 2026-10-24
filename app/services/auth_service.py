from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_random_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.exceptions.errors import ConflictError, UnauthorizedError
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def register(self, data: UserCreate):
        normalized_email = data.email.lower().strip()

        if await self.user_repo.get_by_email(normalized_email):
            raise ConflictError("Email already registered")

        hashed_password = hash_password(data.password)

        user = await self.user_repo.create(
            email=normalized_email, hashed_password=hashed_password
        )

        return user

    async def login(self, data: UserLogin):
        normalized_email = data.email.lower().strip()

        user = await self.user_repo.get_by_email(normalized_email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        now = datetime.now(UTC)
        access_expires_in = settings.expires_in_minutes * 60
        payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "iat": now,
            "exp": now + timedelta(minutes=settings.expires_in_minutes),
        }

        access_token = create_access_token(payload)

        refresh_token = generate_random_token()
        hashed_refresh_token = hash_token(refresh_token)
        refresh_expires_in = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            days=settings.expires_in_days
        )

        await self.auth_repo.create(
            token=hashed_refresh_token, user_id=user.id, expires_at=refresh_expires_in
        )

        return {
            "access_token": access_token,
            "access_expires_in": access_expires_in,
            "refresh_token": refresh_token,
            "refresh_expires_in": refresh_expires_in,
        }

    async def refresh(self, token: str):
        token_hash = hash_token(token)
        session = await self.auth_repo.get_by_token(token=token_hash)
        if not session:
            raise UnauthorizedError("Invalid or revoked refresh token")

        if session.is_revoked:
            await self.auth_repo.revoke_all(session.user_id)
            await self.auth_repo.commit()
            raise UnauthorizedError("Detected reuse token. Revoke all sessions.")

        now = datetime.now(UTC).replace(tzinfo=None)
        if session.expires_at < now:
            revoked = await self.auth_repo.revoke(token=token_hash)
            if not revoked:
                await self.auth_repo.revoke_all(session.user_id)
            await self.auth_repo.commit()
            if not revoked:
                raise UnauthorizedError("Detected reuse token. Revoke all sessions.")
            raise UnauthorizedError("Expired refresh token")

        user = await self.user_repo.get_by_id(session.user_id)
        if not user:
            raise UnauthorizedError("User not found")

        if not await self.auth_repo.revoke(token=token_hash):
            await self.auth_repo.revoke_all(user.id)
            await self.auth_repo.commit()
            raise UnauthorizedError("Detected reuse token. Revoke all sessions.")

        now = datetime.now(UTC)
        access_expires_in = settings.expires_in_minutes * 60
        payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "iat": now,
            "exp": now + timedelta(minutes=settings.expires_in_minutes),
        }

        access_token = create_access_token(payload)
        refresh_token = generate_random_token()
        hashed_refresh_token = hash_token(refresh_token)
        refresh_expires_in = now.replace(tzinfo=None) + timedelta(
            days=settings.expires_in_days
        )

        await self.auth_repo.create(
            token=hashed_refresh_token, user_id=user.id, expires_at=refresh_expires_in
        )

        return {
            "access_token": access_token,
            "access_expires_in": access_expires_in,
            "refresh_token": refresh_token,
            "refresh_expires_in": refresh_expires_in,
        }
