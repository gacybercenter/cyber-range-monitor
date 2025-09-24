'''
range_monitor.core.exceptions

Exceptions that are raised by the application that contain
additional context for diagnosing issues or for providing
more informative error messages to clients.
'''
from fastapi import status


class APIError(Exception):
    '''
    Base exception for custom API exceptions
    '''
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
    '''
    Errors that occur at application runtime that
    are the fault of the application.
    '''

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

class ConnectionFailure(Exception):

    def __init__(
        self,
        service_name: str,
        *,
        reason: str,
        orig_exc: Exception | None = None,
    ) -> None:
        self.service_name = service_name
        self.reason = reason
        self.orig_exc = orig_exc
        message = (
            f'Failed to connect to service {self.service_name}: {self.reason}'
        )
        if self.orig_exc:
            message += f' (original exception: {str(self.orig_exc)})'
        super().__init__(message)