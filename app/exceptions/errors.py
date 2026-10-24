class AppError(Exception):
    """Base class for all errors raise on purpose."""

    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"
    default_message = "Something went wrong"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.message = message or self.default_message
        self.details = details
        self.headers = headers
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"
    default_message = "Bad request"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"
    default_message = "Anthentication required"

    def __init__(self, message: str | None = None, **kwargs):
        # 401 should tell the client which auth scheme to use
        kwargs.setdefault("headers", {"WWW-Authenticate": "Bearer"})
        super().__init__(message, **kwargs)


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    default_message = "You do not have permission"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    default_message = "Resource not found"

    def __init__(self, resource: str | None = None):
        message = None
        if resource is not None:
            message = f"{resource} not found"

        super().__init__(message)


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
    default_message = "Resource already exists"


class UnprocessesableError(AppError):
    status_code = 422
    code = "UNPROCESSABLE"
    default_message = "Cannot process this data"
