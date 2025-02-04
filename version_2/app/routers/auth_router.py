from typing import Annotated
from fastapi import APIRouter, Depends, status, Response, Request

from app.common.dependencies.auth import AdminRequired
from app.schemas.user_schema import CreateUser, UpdateUser, UserResponse, UserDetailsResponse
from app.common.errors import BadRequest, HTTPUnauthorized
from app.core.security import ClientIdentity
from app.common.dependencies import requires_db, session_identity
from app.schemas.session_schema import AuthForm, SessionData
from app.services.security.session_service import SessionAuth
from app.core.config import running_config
from app.common import LogWriter
from app.services.auth_service import AuthService

from app.schemas.generics import ResponseMessage

logger = LogWriter('AUTH')

settings = running_config()
auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
)
auth = AuthService()
session_manager = SessionAuth()


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    auth_form: AuthForm,
    db: requires_db
) -> Response:
    '''_summary_
    Checks the credentials provided by the 'AuthForm'
    and in the response sets a cookie with the session id.

    Arguments:
        request {Request} -- _description_
        auth_form {AuthForm} -- _description_
        db {requires_db} -- _description_

    Raises:
        HTTPUnauthorized: _description_

    Returns:
        Response 
    '''

    client_identity = await ClientIdentity.create(request)

    authenticated_user = await auth.authenticate(auth_form, db)
    if not authenticated_user:
        raise HTTPUnauthorized('Invalid credentials')

    session_data = SessionData.create(
        username=authenticated_user.username,
        role=authenticated_user.role,
        client_identity=client_identity
    )

    signed_session_id = session_manager.create(session_data)
    response = Response(content={'message': 'Login successful'})
    response.set_cookie(
        **settings.cookie_kwargs(signed_session_id)
    )

    return response


@auth_router.post('/logout', response_model=ResponseMessage)
async def logout_user(
    session_id: session_identity,
    response: Response
) -> ResponseMessage:
    '''
    Logs out the user by revoking the refresh token stored in the cookies
    and the access token in the Authorization header if it exists.

    Arguments:
        request {Request}  
        response {Response} 
        token - encoded access token
    Raises:
        HTTPUnauthorizedToken: _description_

    Returns:
        dict 
    '''
    try:
        session_manager.end_session(session_id.signature)
        response.delete_cookie(settings.SESSION_COOKIE)
    except Exception:
        pass
    return ResponseMessage(message='You have successfully logged out')


@auth_router.post(
    '/',
    response_model=UserResponse,
    dependencies=[Depends(AdminRequired())],
    status_code=status.HTTP_201_CREATED
)
async def create_user(create_req: CreateUser, db: requires_db) -> UserResponse:
    '''
    creates a user given the request body schema
    Arguments:
        create_schema {CreateUser} -- the request body schema
    Keyword Arguments:
        db {AsyncSession} - default: {Depends(get_db)})
    Raises:
        HTTPException: 400 - Username is already taken
    Returns:
        UserResponse -- the created user
    '''
    username_taken = await auth.get_username(create_req.username, db)
    if username_taken:
        raise BadRequest('Username is already taken')

    resulting_user = await auth.create_user(db, create_req)
    return resulting_user  # type: ignore


@auth_router.put('/{user_id}', response_model=UserResponse, dependencies=[Depends(AdminRequired())])
async def update_user(
    user_id: int,
    update_req: UpdateUser,
    db: requires_db
) -> UserResponse:
    '''
    updates the user given an id and uses the schema to update the user's data

    Arguments:
        user_id {int} -- user id
        update_schema {UpdateUser} -- the request body schema
    Keyword Arguments:
        db {AsyncSession} -- (default: {Depends(get_db)})
    Returns:
        UserResponse
    '''
    updated_data = await auth.update_user(db, user_id, update_req)
    return updated_data  # type: ignore


@auth_router.delete('/{user_id}')
async def delete_user(
    user_id: int,
    db: requires_db,
    admin: 
) -> dict:
    await user_service.delete_user(db, user_id, admin_user.sub)
    return {'detail': 'User deleted successfully'}


