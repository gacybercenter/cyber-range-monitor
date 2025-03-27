from app.core.errors import HTTPUnauthorized, HTTPForbidden


class HTTPInvalidCredentials(HTTPUnauthorized):
    """Raised when the user provides invalid credentials."""

    def __init__(self) -> None:
        super().__init__(
            msg="Invalid username or password, please try again."
        )


class HTTPApiKeyRequired(HTTPUnauthorized):
    """Raised when an API key is required but not provided."""

    def __init__(self) -> None:
        super().__init__(
            msg="You must be authenticated to access this resource.",
            header={"WWW-Authenticate": "Bearer"}
        )


class HTTPInvalidApiKey(HTTPForbidden):
    """Raised when an invalid API key is provided."""

    def __init__(self) -> None:
        super().__init__(
            msg="Your session has either expired or is invalid, please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
