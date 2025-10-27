from server.app.errors.http import HttpError


class TokenMissingError(HttpError):
    status_code = 401
    code = 'auth_missing'

    def __init__(self) -> None:
        super().__init__(
            detail='auth_required',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidTokenError(HttpError):
    status_code = 401
    code = 'invalid_token'

    def __init__(self, detail: str) -> None:
        super().__init__(
            detail=detail,
            headers={'WWW-Authenticate': f'Bearer error="{detail}"'},
        )


class RoleForbiddenError(HttpError):
    status_code = 403
    code = 'role_forbidden'

    def __init__(self, role: str) -> None:
        super().__init__(detail=f'role_not_allowed={role}')
