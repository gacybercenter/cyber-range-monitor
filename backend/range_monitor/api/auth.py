


from typing import Annotated

from fastapi import APIRouter, Body, Request, status

from range_monitor.users.depends import AuthServiceDep, SessionIdRequired
from range_monitor.users.schema import LoginResponse, UserLoginRequest
from range_monitor.utils.openapi_extra import api_error

auth_router = APIRouter()



@auth_router.post(
    '/login',
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Invalid username or password'),
    },
)
async def login_user(
    request: Request,
    body: Annotated[UserLoginRequest, Body(...)],
    auth_service: AuthServiceDep,
) -> LoginResponse:
    '''
    Authenticates a user when given the proper credentials and stores
    a session to be sent in the `Authorization` header for future requests.
    '''
    authorized_user = await auth_service.check_credentials(
        username=body.username,
        password=body.password
    )
    authentication = await auth_service.authenticate(request, authorized_user)

    return authentication

@auth_router.post(
    '/logout',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('Invalid or expired session'),
    },
)
async def logout_user(
    session_id: SessionIdRequired,
    auth_service: AuthServiceDep,
) -> None:
    '''
    Logs out the current user by invalidating their session when provided with a valid
    session id.
    '''
    await auth_service.end_session(session_id)




