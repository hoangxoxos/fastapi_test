import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, *, token: str, user_id: uuid.UUID, expires_at: datetime
    ) -> Session:
        session = Session(token=token, user_id=user_id, expires_at=expires_at)

        self.db.add(session)
        await self.db.flush()

        return session

    async def get_by_token(self, token: str) -> Session | None:
        result = await self.db.execute(select(Session).where(Session.token == token))
        session = result.scalar_one_or_none()

        return session

    async def get_by_user_id(self, user_id: uuid.UUID) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id)
        )
        session = result.scalar_one_or_none()

        return session

    async def revoke(self, token: str) -> bool:
        result = await self.db.execute(
            update(Session)
            .where(Session.token == token, Session.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        return result.rowcount == 1

    async def revoke_all(self, user_id: uuid.UUID):
        await self.db.execute(
            update(Session).where(Session.user_id == user_id).values(is_revoked=True)
        )
        await self.db.flush()

    async def commit(self) -> None:
        await self.db.commit()
