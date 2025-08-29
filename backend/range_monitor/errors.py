from fastapi import status

from range_monitor.core.exceptions import APIException


class BadRequest(APIException):
    '''
    Raises a 400 Bad Request HttpException
    Error Code - bad_request
    '''
    status_code = status.HTTP_400_BAD_REQUEST
    title = 'Bad Request'
    code = 'bad_request'

    def __init__(self, msg: str) -> None:
        super().__init__(detail=msg)


class ResourceNotFound(APIException):
    '''
    Raises a 404 Not Found HttpException
    '''
    status_code = status.HTTP_404_NOT_FOUND
    title = 'Not Found'
    code = 'not_found'

    def __init__(self, resource_name: str) -> None:
        message = f'{resource_name} not found'
        super().__init__(detail=message)


class UnauthorizedAccess(APIException):
    '''
    Raises a 401 Unauthorized HttpException
    Error Code - unauthorized_access
    '''
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Unauthorized Access'
    code = 'unauthorized_access'

    def __init__(self, msg: str | None = None) -> None:
        msg_default = 'You are not authorized to access this resource'
        super().__init__(detail=msg or msg_default)


class ForbiddenAccess(APIException):
    '''
    Raises a 403 Forbidden HttpException
    error code - forbidden_access
    '''

    status_code = status.HTTP_403_FORBIDDEN
    title = 'Forbidden Access'
    code = 'forbidden_access'

    def __init__(
        self,
        detail: str | None = None,
        headers: dict | None = None
    ) -> None:
        detail_default = 'You do not have permission to access this resource'
        super().__init__(detail=detail or detail_default, headers=headers)


class UnprocessableEntity(APIException):
    '''
    Raises a 422 Unprocessable Entity HttpException
    error code - unprocessable_entity
    '''
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    title = 'Unprocessable Entity'
    code = 'unprocessable_entity'

    def __init__(self, msg: str) -> None:
        super().__init__(detail=msg)


