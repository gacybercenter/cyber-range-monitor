from fastapi import status

from monitor_api.core.exceptions import APIException


class BadRequest(APIException): ...


class ResourceNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    title = 'Not Found'
    code = 'not_found'

    def __init__(self, resource_name: str) -> None:
        message = f'{resource_name} not found'
        super().__init__(detail=message)


class UnauthorizedAccess(APIException):
    """Raises a 401 Unauthorized HttpException - HttpErrorLabel.INVALID_PERMISSIONS"""

    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Unauthorized Access'
    code = 'unauthorized_access'

    def __init__(self, msg: str | None = None) -> None:
        msg_default = 'You are not authorized to access this resource'
        super().__init__(detail=msg or msg_default)


class ForbiddenAccess(APIException):
    """Raises a 403 Forbidden HttpException"""

    status_code = status.HTTP_403_FORBIDDEN
    title = 'Forbidden Access'
    code = 'forbidden_access'

    def __init__(self, msg: str | None = None) -> None:
        msg_default = 'You do not have permission to access this resource'
        super().__init__(detail=msg or msg_default)




class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    title = 'Unprocessable Entity'
    code = 'unprocessable_entity'

    def __init__(self, msg: str) -> None:
        super().__init__(detail=msg)
