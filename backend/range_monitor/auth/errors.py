from range_monitor.core.errors import APIError


class AuthMissing(APIError):
    status_code = 401
    code = 'auth_missing'

    def __init__(self) -> None:
        super().__init__(
            detail='auth_required',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidJwtToken(APIError):
    status_code = 401
    code = 'invalid_token'

    def __init__(self, detail: str) -> None:
        super().__init__(
            detail=detail,
            headers={'WWW-Authenticate': f'Bearer error="{detail}"'},
        )


class DoubleRotationConflict(APIError):
    status_code = 409
    code = 'double_rotation_conflict'

    def __init__(self) -> None:
        super().__init__(
            detail='double_rotation_conflict',
        )


class RoleForbidden(APIError):
    status_code = 403
    code = 'role_forbidden'

    def __init__(self, role) -> None:
        super().__init__(detail=f'role_not_allowed={role}')
