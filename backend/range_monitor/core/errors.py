"""
range_monitor.core.errors

Exceptions that are raised by the application that contain
additional context for diagnosing issues or for providing
more informative error messages to clients.
"""

from fastapi import status


class APIError(Exception):
    """
    Base exception for custom API exceptions
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = 'bad_request'

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


class RuntimeAppError(RuntimeError):
    """
    Errors that occur at application runtime that
    are the fault of the application.

    If it occurs during a request, it should be logged and the
    client should receive a `503 Service Unavailable`.
    """

    def __init__(
        self,
        code: str,
        reason: str | None = None,
        fix: str | None = None,
    ) -> None:
        self.reason = reason or 'Not specified'
        self.fix = fix or 'Not specified'
        self.code = code
        message = f'[{self.code}] {self.reason} (fix: {self.fix})'
        super().__init__(message)


class DatabaseFailure(Exception):
    """
    Exception raised for unhandled database errors.

    Should be caught at the service layer and logged
    and turned into a `424 Failed Dependency` response.
    """

    def __init__(
        self,
        *,
        table_name: str,
        operation: str,
        orig_exc: Exception,
    ) -> None:
        self.table_name = table_name
        self.operation = operation
        self.orig_exc = orig_exc
        message = (
            f'An unhandled database error occured on table {self.table_name} '
            f'during operation `{self.operation}`: {str(self.orig_exc)}'
        )
        super().__init__(message)


class HttpTransportViolation(Exception):
    """
    Exception raised when an HTTP transport violation occurs.
    Such as attempting to send a request to a non-HTTPS URL
    should never happen, but if it does, this exception
    provides context about the violation.
    """

    def __init__(
        self,
        requested_url: str,
        *,
        tenant: str,
        reason: str,
    ) -> None:
        self.tenant = tenant
        self.reason = reason
        message = (
            f'Cannot send request to {requested_url} for tenant '
            f'{self.tenant}: {self.reason}'
        )
        super().__init__(message)
