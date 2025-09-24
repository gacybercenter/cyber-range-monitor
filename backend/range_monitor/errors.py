from fastapi import status

from range_monitor.core.errors import APIError


class BadRequest(APIError):
    '''
    Raises a 400 Bad Request HttpException
    Error Code - bad_request
    '''
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'bad_request'

    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail)


class ResourceNotFound(APIError):
    '''
    Raises a 404 Not Found HttpException
    '''
    status_code = status.HTTP_404_NOT_FOUND
    code = 'not_found'

    def __init__(self, resource_name: str) -> None:
        super().__init__(detail=f'{resource_name}_not_found')


class UnauthorizedAccess(APIError):
    '''
    Raises a 401 Unauthorized HttpException
    Error Code - unauthorized_access
    '''
    status_code = status.HTTP_401_UNAUTHORIZED
    code = 'unauthorized_access'

    def __init__(self, detail: str | None = None) -> None:
        msg_default = 'You are not authorized to access this resource'
        super().__init__(detail=detail or msg_default)


class ForbiddenError(APIError):
    '''
    Raises a 403 Forbidden HttpException
    error code - forbidden_access
    '''

    status_code = status.HTTP_403_FORBIDDEN
    code = 'forbidden_access'

    def __init__(
        self,
        detail: str | None = None,
        headers: dict | None = None
    ) -> None:
        detail_default = 'You do not have permission to access this resource'
        super().__init__(detail=detail or detail_default, headers=headers)


class UnprocessableEntity(APIError):
    '''
    Raises a 422 Unprocessable Entity HttpException
    error code - unprocessable_entity
    '''
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = 'unprocessable_entity'

    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail)

class ConflictError(APIError):
    '''
    Raises a 409 Conflict HttpException
    error code - conflict_error
    '''
    status_code = status.HTTP_409_CONFLICT
    code = 'conflict_error'

    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail)

class EmptyPatchError(APIError):
    '''
    Raises a 400 Bad Request HttpException for empty patch requests
    error code - empty_patch
    '''
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'empty_patch'

    def __init__(self) -> None:
        super().__init__(detail='no_fields_provided')