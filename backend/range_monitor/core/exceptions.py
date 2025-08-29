from fastapi import status

# Custom Http Exceptions & Shorthands



class APIException(Exception):
    '''
    Base exception for custom API exceptions
    '''
    status_code: int = status.HTTP_400_BAD_REQUEST
    title: str = 'Bad Request'
    code: str = 'bad_request'

    def __init__(
        self,
        *,
        detail: str | None = None,
        headers: dict | None = None,
        extras: dict | None = None,
    ) -> None:
        self.detail = detail or self.title
        self.headers = headers or {}
        self.extras = extras or {}
        super().__init__(self.detail)

class AdapaterError(RuntimeError):
    """Base exception for adapter errors"""


class AdapterNotConnectedError(AdapaterError):
    """Raised when an adapter is not connected but an operation requiring
    a connection is attempted"""

    def __init__(
        self,
        *,
        adapter_name: str,
    ) -> None:
        super().__init__(
            f'Cannot use Adapter `{adapter_name}` because it was never connected'
        )


class AdapterConnectionError(AdapaterError):
    """Raised when an adapter fails to connect"""

    def __init__(
        self,
        *,
        adapter_name: str,
        exc: Exception,
    ) -> None:
        super().__init__(
            f'Could not connect `{adapter_name}` due to encountering exception: '
            f'{exc.__class__.__name__} while trying to connect it. Details: {exc}'
        )