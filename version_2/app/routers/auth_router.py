from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.responses import JSONResponse


from app.common.dependencies import AdminRequired
from app.common.errors import BadRequest, HTTPForbidden, HTTPNotFound, HTTPUnauthorized
from app.services.security.session_service import SessionService
from app.services.auth_service import AuthService
from app.common.dependencies import (
    requires_db, 
    client_identity, 
    admin_required, 
    role_required,
    SessionAuth
)
from app.schemas.user_schema import (
    AuthForm, 
    CreateUserBody, 
    UserResponse, 
    UserDetailsResponse,
    UpdateUserBody
)
from app.schemas.session_schema import SessionData
from app.core.config import running_config
from app.common import LogWriter

from app.common.models import ResponseMessage

logger = LogWriter('AUTH')

settings = running_config()
auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
)

auth = AuthService()
session_manager = SessionService()


@auth_router.post('/login')
async def login(
    client: client_identity,
    auth_form: AuthForm,
    db: requires_db
) -> JSONResponse:
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

    authenticated_user = await auth.authenticate(auth_form, db)
    if not authenticated_user:
        raise HTTPUnauthorized('Invalid credentials')

    session_data = SessionData.create(
        username=authenticated_user.username,
        role=authenticated_user.role,
        client_identity=client
    )

    session_signature = session_manager.create(session_data)
    response = JSONResponse(
        content={'message': 'Login successful'}
    )
    response.set_cookie(
        **settings.cookie_kwargs(session_signature)
    )
    return response


@auth_router.post('/logout', dependencies=[Depends(SessionAuth)])
async def logout_user(request: Request) -> JSONResponse:
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
    response = JSONResponse(content={'message': 'Logout successful'})
    try:
        session_signature = request.cookies.get(settings.SESSION_COOKIE)
        await SessionAuth.revokes(session_signature, response)
    except Exception:
        pass
    return response


@auth_router.post(
    '/',
    response_model=UserResponse,
    dependencies=[Depends(AdminRequired())],
    status_code=status.HTTP_201_CREATED
)
async def create_user(create_req: CreateUserBody, db: requires_db) -> UserResponse:
    '''
    creates a user given the request body schema
    Arguments:
        create_schema {CreateUserBody} -- the request body schema
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


@auth_router.put(
    '/{user_id}', 
    response_model=UserResponse, 
    dependencies=[Depends(AdminRequired())]
)
async def update_user(
    user_id: int,
    update_req: UpdateUserBody,
    db: requires_db
) -> UserResponse:
    '''_summary_
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
    admin: admin_required
) -> dict:
    await auth.delete_user(db, user_id, admin.username)
    return ResponseMessage(message='User deleted')  # type: ignore


@auth_router.get('/{user_id}', response_model=UserResponse)
async def read_user(
    user_id: int,
    db: requires_db,
    reader: role_required
) -> UserResponse:
    user = await auth.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')

    if not (reader.role >= user.role):
        raise HTTPForbidden('Cannot read a user with higher permissions')

    return user  # type: ignore


@auth_router.get('/all', response_model=list[UserResponse])
async def public_read_all(
    db: requires_db,
    reader: role_required
) -> list[UserResponse]:
    users = await auth.role_based_read_all(reader.role, db)

    return users  # type: ignore


@auth_router.get(
    '/details',
    dependencies=[Depends(AdminRequired())],
    response_model=list[UserDetailsResponse]
)
async def read_all_user_details(db: requires_db) -> list[UserDetailsResponse]:
    users = await auth.get_all(db)
    return users  # type: ignore


@auth_router.get(
    '/details/{user_id}',
    dependencies=[Depends(AdminRequired())],
    response_model=UserDetailsResponse
)
async def read_user_details(user_id: int, db: requires_db) -> UserDetailsResponse:
    user = await auth.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')
    return user  # type: ignore





