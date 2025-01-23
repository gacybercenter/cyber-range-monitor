from enum import StrEnum
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Any


from api.db.main import get_session
from api.db.logging import LogWriter


logger = LogWriter('ERRORS')


class ErrorTypes(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    SYSTEM_ERROR = "SYSTEM_ERROR"

SEVERITY_MAP = {
    ErrorTypes.VALIDATION_ERROR: 2,
    ErrorTypes.AUTHENTICATION_ERROR: 3,
    ErrorTypes.AUTHORIZATION_ERROR: 3,
    ErrorTypes.NOT_FOUND: 1,
    ErrorTypes.SYSTEM_ERROR: 10
}



class APIErrorResponse(BaseModel):
    error_type: ErrorTypes
    message: str
    details: dict[str, Any] = {}


def handle_validation_error(
    exc: ValidationError,
) -> JSONResponse:
    error_details = {}
    for error in exc.errors():
        field_path = " -> ".join(str(x) for x in error["loc"])
        error_details[field_path] = {
            'message': error.get('msg', ''),
            'input': error.get('input', '')
        }
        
    response_content = APIErrorResponse(
        error_type=ErrorTypes.VALIDATION_ERROR,
        message='Validation error',
        details=error_details
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response_content.model_dump()
    )


def label_status_code(exc: HTTPException) -> ErrorTypes:
    '''
    returns a standardized JSON response for all HTTP exceptions
    Returns:
        JSONResponse -- _description_
    '''
    error_type = ErrorTypes.SYSTEM_ERROR
    
    match exc.status_code:
        case status.HTTP_404_NOT_FOUND:
            error_type = ErrorTypes.NOT_FOUND

        case status.HTTP_401_UNAUTHORIZED:
            error_type = ErrorTypes.AUTHENTICATION_ERROR

        case status.HTTP_403_FORBIDDEN:
            error_type = ErrorTypes.AUTHORIZATION_ERROR

        case _:
            error_type = ErrorTypes.SYSTEM_ERROR

    return error_type


def register_exc_handlers(app: FastAPI) -> None:
    '''
    Standardizes the response from the API when an exception is raised
    and implements logging for common client side exceptions.
    
    
    Arguments:
        app {FastAPI} -- the app to register the exception handlers to

    Returns:
        void
    '''
    
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_, exc) -> JSONResponse:
        '''
        Logs & resolves a validation error into something easier to process 
        for the front end in the standard APIErrorResponse format
    
        Returns:
            JSONResponse -- a json response with the status code and error message
        '''
        async with get_session() as session:
            await logger.warning(f'A validation error occured... ({exc})', session)
        return handle_validation_error(exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        '''
        returns a standardized JSON response for all HTTP exceptions and gives a 
        verbose log of the request that caused the exception for Internal Server Errors 
        Returns:
            JSONResponse -- a json response with the status code and error message
        '''
        log_msg = f'An HTTP error occured {exc.__repr__()} {request.url.path} ({request.method})'
        error_type = label_status_code(exc)
        async with get_session() as session:
            await logger.error(log_msg, session)
            if SEVERITY_MAP[error_type] == 10:
                verbose_request = (
                    f'URL={request.url} METHOD={request.method} '
                    f'HOST={request.client.host if request.client else "unknown"} '
                    f'PORT={request.client.port if request.client else "unknown"} '
                    f'HEADERS={request.headers}'
                )
                await logger.critical(verbose_request, session)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=APIErrorResponse(
                error_type=error_type,
                message=exc.detail
            ).model_dump()
        )
            
        
        
        
        
        
        
        