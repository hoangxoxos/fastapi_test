from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.deps import CurrentUser, get_auth_service
from app.core.config import settings
from app.core.rate_limit import limiter
from app.exceptions.errors import UnauthorizedError
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserReadPublic
from app.services.auth_service import AuthService

router = APIRouter()


def _set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=int(timedelta(days=settings.expires_in_days).total_seconds()),
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie("refresh_token", path="/auth")


@router.post(
    "/register", response_model=UserReadPublic, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.register(data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    data: UserLogin,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    result = await service.login(data)

    _set_refresh_cookie(response, token=result["refresh_token"])

    return TokenResponse(
        access_token=result["access_token"], expires_in=result["access_expires_in"]
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise UnauthorizedError("No refresh token found")

    result = await service.refresh(token)

    _set_refresh_cookie(response, token=result["refresh_token"])
    return TokenResponse(
        access_token=result["access_token"], expires_in=result["access_expires_in"]
    )


@router.get("/me", response_model=UserReadPublic, status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUser):
    return user
