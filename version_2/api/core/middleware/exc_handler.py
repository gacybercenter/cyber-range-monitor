from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from enum import StrEnum
import json
from fastapi.exceptions import RequestValidationError
import traceback


from api.db.main import get_session
from api.core.logging import LogWriter


logger = LogWriter('ERRORS')
FLAGGED_STATUS_CODES = {403, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417}


class ErrorLabel(StrEnum):
    '''
    Included in the logs to categorize http exceptions, even slightly suspicious status codes 
    such as 405 method not allowed should be flagged since it could indicate enumeration / probing

    Arguments:
        StrEnum {_type_} -- _description_
    '''

    USER_ERROR = 'USER_ERROR'
    SECURITY_FLAG = 'SECURITY_FLAG'
    SYSTEM_ERROR = 'SYSTEM_ERROR'


SEVERITY_MAP = {
    ErrorLabel.USER_ERROR: 1,
    ErrorLabel.SECURITY_FLAG: 2,
    ErrorLabel.SYSTEM_ERROR: 3
}


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
    error_label: ErrorLabel = Field(
        ..., description="A label for the error type to make it easier to filter logs"
    )

    def __repr__(self) -> str:
        return f"status_code={self.status_code}, api_path={self.api_path}, method={self.method}, exc_details={self.exc_details}, error_label={self.error_label}"


class VerboseHTTPErrorMeta(HTTPErrorMeta):
    client_ip: str = Field(
        ..., description="The IP address of the client making the request"
    )
    user_agent: str = Field(
        ..., description="The User-Agent string of the client making the request"
    )
    headers: str = Field(
        ..., description="The jsonified headers of the request that caused the error")
    stack_trace: str = Field(
        ..., description="The stack trace of the error that was raised"
    )

    def __repr__(self) -> str:
        return super().__repr__() + f", client_ip={self.client_ip}, user_agent={self.user_agent}, headers={self.headers}, stack_trace={self.stack_trace}"


class APIErrorResponse(BaseModel):
    message: str = Field(
        ..., description="A description of the error that occured for the frontend to display")
    success: bool = False

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"


class InvalidRequestResponse(BaseModel):
    success: bool = False
    errors: list[dict[str, str]] = Field(
        ..., description="A list of errors that occured during the request validation"
    )

    def __repr__(self) -> str:
        error_strs = [
            f"{error['loc'][0]}={error['msg']}" for error in self.errors
        ]
        return f"InvalidRequestResponse(errors=[{', '.join(error_strs)}])"


class ErrorService:
    def _label_status_code(self, exc: HTTPException) -> ErrorLabel:
        '''assigns a label for logging purposes to classify the error types'''
        if exc.status_code >= 500:
            return ErrorLabel.SYSTEM_ERROR

        if exc.status_code in FLAGGED_STATUS_CODES:
            return ErrorLabel.SECURITY_FLAG

        return ErrorLabel.USER_ERROR

    def _get_error_meta(self, request: Request, exc: HTTPException) -> HTTPErrorMeta:
        '''
        Gets the error 'meta data' for an HTTP exception so it can be logged and handled 
        accordingly

        Arguments:
            request {Request} 
            exc {HTTPException} 

        Returns:
            HTTPErrorMeta | VerboseHTTPErrorMeta -- the error meta data
        '''

        error_label = self._label_status_code(exc)
        base_error_meta = {
            'status_code': exc.status_code,
            'api_path': request.url.path,
            'method': request.method,
            'exc_details': exc.detail,
            'error_label': error_label
        }
        if error_label != ErrorLabel.SYSTEM_ERROR:
            return HTTPErrorMeta(**base_error_meta)

        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = request.client.host if request.client else "unknown"
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
    
        fmt_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return VerboseHTTPErrorMeta(
            **base_error_meta,
            client_ip=client_ip,
            user_agent=request.headers.get('user-agent', 'unknown'),
            headers=json.dumps(dict(request.headers)),
            stack_trace=fmt_traceback
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

    
    
    async def log_error_meta(self, error_meta: HTTPErrorMeta, db: AsyncSession) -> str:
        meta_str = json.dumps(error_meta.model_dump())
        if error_meta.error_label != ErrorLabel.SYSTEM_ERROR:
            await logger.error(
                f'An HTTP error occured with the following meta data: {meta_str}',
                db, 
                label=error_meta.error_label.value
            )     
            return error_meta.exc_details
        
        await logger.critical(
            f'{ErrorLabel.SYSTEM_ERROR} - An Internal Server Error has occured: {meta_str}', 
            db    
        )
        return 'Something went wrong, please try again or contact an adminstrator if this issue persists.'


    async def process_http_error(self, request: Request, exc: HTTPException) -> JSONResponse:
        '''
        Processes an HTTP exception to get the error meta data and logs it
        Arguments:
            request {Request} -- the request that caused the exception
            exc {HTTPException} -- the exception that was raised

        Returns:
            JSONResponse -- a json response with the status code and error message
        '''
        error_meta = self._get_error_meta(request, exc)
        async with get_session() as session:
            response_msg = await self.log_error_meta(error_meta, session)
        
        
        
        status_code = exc.status_code 
        if status_code >= 500:
            status_code = status.HTTP_400_BAD_REQUEST
        
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )
        
        
        
        
            
            
            
            
            
            
        
        
        
        
        
        
        return JSONResponse(
            status_code=exc.status_code,
            content=APIErrorResponse(
                message=exc.detail
            ).model_dump()
        )
    
    
    
    
    
    
    
def register_exc_handlers(app: FastAPI) -> None:
    '''
    Stanardizes the response from the API when an exception is raised
    and implements logging for common client side exceptions.


    Arguments:
        app {FastAPI} -- the app to register the exception handlers to

    Returns:
        void
    '''

    err_service = ErrorService()

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        async with get_session() as session:
            await logger.warning(f'A validation error occured... ({exc})', session)
            err_data = normalize_pydantic_errors(exc)
            await logger.error(f'ERROR_META: {err_data}', session)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
        print('i am in http handler')

        log_msg = f'An HTTP error occured {exc} {
            request.url.path} - ({request.method})'
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
