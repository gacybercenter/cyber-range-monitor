from fastapi import HTTPException, status

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

class TooManyRequests(APIError):
    '''
    Raises a 429 Too Many Requests HttpException
    error code - too_many_requests
    '''
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = 'too_many_requests'

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail or 'rate_limit_exceeded')


class DatasourceNotEnabled(APIError):
    '''
    Raises a 503 Service Unavailable HttpException
    error code - datasource_unreachable
    '''
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = 'datasource_unreachable'

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail or 'datasource_unreachable')


class InvalidDatasourceGateway(APIError):
    '''
    Raises a 502 Bad Gateway HttpException
    error code - invalid_datasource_gateway
    '''
    status_code = status.HTTP_502_BAD_GATEWAY
    code = 'invalid_datasource_gateway'

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail or 'invalid_datasource_gateway')



class GatewayTimeout(APIError):
    '''
    Raises a 504 Gateway Timeout HttpException
    error code - gateway_timeout
    '''
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    code = 'gateway_timeout'

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail or 'gateway_timeout')


class SeeOther(HTTPException):
    '''
    Raises a 303 See Other HttpException
    '''
    def __init__(self, location: str) -> None:
        super().__init__(
            status_code=status.HTTP_303_SEE_OTHER,
            detail='see_other',
            headers={'Location': location}
        )