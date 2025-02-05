from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from enum import StrEnum
import json
from fastapi.exceptions import RequestValidationError
import traceback


from app.core.db import get_session
from app.common.logging import LogWriter
from app.core.security.models import ClientIdentity


logger = LogWriter('ERRORS')
FLAGGED_STATUS_CODES = {403, 405, 406, 407, 408,
                        409, 410, 411, 412, 413, 414, 415, 416, 417}



class HTTPErrorMeta(BaseModel):
    status_code: int = Field(
        ..., description="The HTTP status code of the error")
    api_path: str = Field(..., description="The API path that was accessed")
    method: str = Field(
        ..., description="The HTTP method used for the request"
    )
    exc_details: str = Field(
        ..., description="The details of the exception that was raised"
    )

    def __repr__(self) -> str:
        return f"A HTTP ({self.status_code}) Exception was raised\nContext: api_path={self.api_path}, method={self.method}, exc_details={self.exc_details}"


class HTTPTraceback(HTTPErrorMeta):
    headers: str = Field(
        ..., 
        description="The jsonified headers of the request that caused the error"
    )
    stack_trace: str = Field(
        ..., 
        description="The stack trace of the error that was raised"
    )
    client_identity: ClientIdentity = Field(..., description="The identity of the client that caused the error")

    def __repr__(self) -> str:
        return super().__repr__() + f"Internal Server Error\nHeaders:\n\t{self.headers}, StackTrace:\n\t{self.stack_trace}Client Identity:\n\t{self.client_identity}"


class APIErrorResponse(BaseModel):
    message: str = Field(
        ..., 
        description="A description of the error that occured for the frontend to display"
    )
    success: bool = False

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"


class InvalidRequestResponse(BaseModel):
    success: bool = False
    errors: list[dict[str, str]] = Field(
        ..., 
        description="A list of errors that occured during the request validation"
    )

    def __repr__(self) -> str:
        error_strs = [
            f"{error['loc'][0]}={error['msg']}" for error in self.errors
        ]
        return f"InvalidRequestResponse(errors=[{', '.join(error_strs)}])"


class ErrorService:
    async def _get_error_meta(self, request: Request, exc: HTTPException) -> HTTPErrorMeta:
        '''
        Gets the error 'meta data' for an HTTP exception so it can be logged and handled 
        accordingly

        Arguments:
            request {Request} 
            exc {HTTPException} 

        Returns:
            HTTPErrorMeta | HTTPTraceback -- the error meta data
        '''

        base_error_meta = {
            'status_code': exc.status_code,
            'api_path': request.url.path,
            'method': request.method,
            'exc_details': exc.detail,
        }
        
        if not (exc.status_code in FLAGGED_STATUS_CODES or exc.status_code >= 500):
            return HTTPErrorMeta(**base_error_meta)
        
        client_identity = await ClientIdentity.create(request)
        fmt_traceback = ''.join(traceback.format_exception(
                type(exc), 
                exc, 
                exc.__traceback__
            )
        )
        return HTTPTraceback(
            **base_error_meta,
            headers=json.dumps(dict(request.headers)),
            stack_trace=fmt_traceback,
            client_identity=client_identity
        )

    def normalize_pydantic_errors(self, exc: RequestValidationError) -> InvalidRequestResponse:
        '''
        Normalizes and standardizes how pydantic validation errors are returned to the client 
        (the default formatting is very hard to read and understand)
        Arguments:
            exc {RequestValidationError} -- the exception to normalize

        Returns:
            InvalidRequestResponse -- the normalized error response
        '''

        errors = []
        for error in exc.errors():
            errors.append({
                'field': error['loc'][0],
                'error': error['msg']
            })
        return InvalidRequestResponse(errors=errors)

    async def log_error_meta(self, error_meta: HTTPErrorMeta, db: AsyncSession) -> None:
        if error_meta.status_code >= 500:
            await logger.critical(
                json.dumps(error_meta.model_dump()),
                db
            )
        elif error_meta.status_code in FLAGGED_STATUS_CODES:
            await logger.error(error_meta.__repr__(), db)   
        else:
            await logger.warning(error_meta.__repr__(), db)   

    async def process_http_error(self, request: Request, exc: HTTPException) -> JSONResponse:
        '''
        Processes an HTTP exception to get the error meta data and logs it
        Arguments:
            request {Request}-- the request that caused the exception
            exc {HTTPException} -- the exception that was raised

        Returns:
            JSONResponse -- a json response with the status code and error message
        '''
        error_meta = await self._get_error_meta(request, exc)
        async with get_session() as session:
            response_msg = await self.log_error_meta(error_meta, session)
        status_code = exc.status_code
        if status_code >= 500:
            # obfuscate the error status from the client 
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content=APIErrorResponse(
                    message='Oops, something went wrong which caused the server to timeout. Please try again our contact an admin if the problem persists.'
                ).model_dump()
            )
            
        response = APIErrorResponse(message=exc.detail)
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )


def register_exc_handlers(app: FastAPI) -> None:
    '''
    Stanardizes the response from the API when an exception is raised
    and implements logging for common client side exceptions.


    Arguments:
        app {FastAPI} -- the app to register the exception handlers to

    Returns:
        void    '''

    err_service = ErrorService()

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        async with get_session() as session:
            await logger.warning(f'A validation error occured... ({exc})', session)
            err_data = err_service.normalize_pydantic_errors(exc)
            await logger.error(f'ERROR_META: {err_data}', session)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=err_data.model_dump()
            )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        '''
        returns a standardized JSON response for all HTTP exceptions and gives a 
        verbose log of the request that caused the exception for Internal Server Errors 
        Returns:
            JSONResponse -- a json response with the status code and error message
        '''
        return await err_service.process_http_error(request, exc)        
