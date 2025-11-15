"""
Exceptions that are raised by the application for utility purposes
or for catching specific error types.
"""

from fastapi import status
from pydantic import ValidationError


class AppError(Exception): ...


def _stringify_pydantic_error(err: ValidationError) -> str:
    from server.schema import parse_pydantic_error

    errors = []
    for e in err.errors():
        parsed = parse_pydantic_error(e)
        errors.append(
            f'Field({parsed["type"]}): {parsed["field"]}\nDetail: {parsed["detail"]} '
        )
    return '\n'.join(errors)


class RuntimeValidationError(AppError):
    def __init__(self, orig_exc: ValidationError) -> None:
        self.orig_exc = orig_exc
        super().__init__(_stringify_pydantic_error(orig_exc))


class StartupError(AppError):
    """
    Raised when there is an error during application startup
    """


class HttpError(AppError):
    """
    Base exception for custom API exceptions
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = 'internal_server_error'

    def __init__(
        self,
        *,
        detail: str | None = None,
        headers: dict | None = None,
        extras: dict | None = None,
    ) -> None:
        self.detail = detail or 'error_not_labeled'
        self.headers = headers or {}
        self.extras = extras or {}
        super().__init__(self.detail)
