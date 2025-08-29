from fastapi import Request
from fastapi.security import HTTPBearer

from range_monitor.core.exceptions import APIException
from range_monitor.depends import SignatureDep
from range_monitor.users.sessions import constant


class AuthenticationRequired(APIException):
    status_code = 401
    title = 'Authentication Required'
    code = 'not_authenticated'


class AuthenticationExpired(APIException):
    status_code = 401
    title = 'Authentication Expired'
    code = 'session_expired'


class HTTPSessionBearer(HTTPBearer):
    def __init__(self) -> None:
        super().__init__(
            scheme_name=constant.BEARER_SCHEME_NAME,
            description=constant.BEARER_DESCRIPTION,
            auto_error=False,
        )
        self.max_age: int = int(constant.SESSION_MAX_AGE.total_seconds())

    async def __call__(self, request: Request, signer: SignatureDep) -> str:
        """
        Retrieves the signed session id from the Authorization header,
        and then verifies it hasn't reached the max age and returns the
        session token.

        Parameters
        ----------
        request : Request

        Returns
        -------
        str
            _The unsigned session_

        Raises
        ------
        AuthenticationRequired
            _Session ID missing, improper auth scheme or invalid signature_
        """
        auth = await super().__call__(request)
        if not auth:
            raise AuthenticationRequired(
                detail='You must be authenticated to continue.',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        unsigned_sid = signer.get_message(auth.credentials, max_age=self.max_age)

        if not unsigned_sid:
            raise AuthenticationExpired(
                detail='Invalid or expired session, please log in again.',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return unsigned_sid
