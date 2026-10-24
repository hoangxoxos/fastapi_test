from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_access_token
from app.exceptions.errors import ForbiddenError, UnauthorizedError
from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer()

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_auth_service(db: DbSession) -> AuthService:
    # db -> repository -> service
    return AuthService(UserRepository(db), AuthRepository(db))


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: DbSession,
):

    token = credentials.credentials

    if not token:
        raise UnauthorizedError("Could not validate credentials")

    try:
        payload = verify_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise UnauthorizedError("Invalid token")

    try:
        user_id = UUID(subject)
    except ValueError:
        raise UnauthorizedError("Invalid token")

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
