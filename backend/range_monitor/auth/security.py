
from fastapi import Request, status
from fastapi.security import HTTPBearer

from range_monitor.auth import constant
from range_monitor.core.errors import APIException


class MissingTokenClaim(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Missing Token Claim'
    code = 'token_missing'

    def __init__(
        self,
        *,
        detail: str,
        headers: dict
    ) -> None:
        super().__init__(detail=detail, headers=headers)




class JwtTokenBearer(HTTPBearer):
    def __init__(self) -> None:
        super().__init__(
            scheme_name=constant.BEARER_SCHEME_NAME,
            description=constant.BEARER_DESCRIPTION,
            auto_error=False,
        )


    async def __call__(self, request: Request) -> str:
        auth = await super().__call__(request)
        if auth is None:
            raise MissingTokenClaim(
                detail='Authorization header is missing.',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        return auth.credentials







