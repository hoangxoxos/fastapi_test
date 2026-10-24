import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.errors import AppError

logger = logging.getLogger(__name__)


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details=None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
        headers=headers,
    )


async def app_error_handler(request: Request, exc: AppError):
    return _error_response(
        exc.status_code, exc.code, exc.message, exc.details, exc.headers
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Errors from FastAPI itself (for example, route not found -> 404)
    return _error_response(
        exc.status_code, "HTTP_ERROR", str(exc.detail), headers=exc.headers
    )


async def unhandled_error_handler(request: Request, exc: Exception):
    # Unknown bug. Log it, but do NOT show details to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _error_response(500, "INTERNAL_ERROR", "Internal Server Error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
