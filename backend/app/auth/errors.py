from fastapi import HTTPException


class HTTPInvalidOrExpiredSession(HTTPException):
    """An exception to raise when a session is invalid"""

    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Your session is invalid or has expired")
