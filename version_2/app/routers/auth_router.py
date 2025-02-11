from typing import Annotated
from fastapi import APIRouter, Body, Depends, Form, status, Response, Request
from fastapi.responses import JSONResponse


from app.common.errors import BadRequest, HTTPForbidden, HTTPNotFound, HTTPUnauthorized

from app.schemas.user_schema import (
    AuthForm, 
    CreateUserForm, 
    UpdateUserForm, 
    UserDetailsResponse,
    UserResponse
)
from app.services.auth import AuthService, SessionService
from app.common.dependencies import (
    AdminRequired,
    SessionAuth,
    DatabaseRequired,
    IdentityRequired,
    AdminProtected,
    CurrentUser,
)

from app.schemas.session_schema import SessionData
from app.config import running_config
from app.common.logging import LogWriter
from app.common.models import ResponseMessage

logger = LogWriter('AUTH')

settings = running_config()
auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication', 'Users']
)

auth = AuthService()
session_manager = SessionService()


@auth_router.post('/login/')
async def login(
    auth_form: Annotated[AuthForm, Form(...)],
    client: IdentityRequired,
    db: DatabaseRequired
) -> JSONResponse:
    '''Checks the credentials provided by the 'AuthForm'
    and in the response sets a cookie with the session id when given
    valid login credentials.

    Arguments:
        request {Request} -- _description_
        auth_form {AuthForm} -- Has types to enforce constraints on the request body
        db {requires_db} -- _description_

    Raises:
        HTTPUnauthorized: _description_

    Returns:
        Response 
    '''

    authenticated_user = await auth.authenticate(auth_form, db)
    if not authenticated_user:
        raise HTTPUnauthorized('Invalid username or password')

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
    '''[AUTH] - Logs out the user using the "SessionAuth" (SessionAuthority) 
    to load the clients signed session id and fetches and decrypts the SessionData 
    from Redis, if the session hasn't been tampered with by the user and is valid the 
    session is revoked by deleting the key in the Redis store mapped to the unsigned
    session id and the cookie is removed from the client  
    
    
    Arguments:
        request {Request}  - the request to get the existing session ID from
    Raises:
        If the session ID is not found or the session was tampered with 
        by the client 
    Returns:
        JSONResponse -- a message indicating the logout was successful
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
async def create_user(
    create_req: Annotated[CreateUserForm, Form(...)],
    db: DatabaseRequired
) -> UserResponse:
    '''[ADMIN] - Creates a user given valid form data and inserts
    the created user into the database and returns the 
    created user 
    
    Arguments:
        create_schema {CreateUserForm} -- the form data
        db {AsyncSession} - the database session
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
    '/user/{user_id}/',
    response_model=UserResponse,
    dependencies=[Depends(AdminRequired())],
    status_code=status.HTTP_202_ACCEPTED
)
async def update_user(
    user_id: int,
    update_req: Annotated[UpdateUserForm, Form()],
    db: DatabaseRequired
) -> UserResponse:
    '''updates the user given an id and uses the schema to update the user's data

    Arguments:
        user_id {int} -- user id of the user to update
        update_schema {UpdateUser} -- the request body schema
        db {AsyncSession} -- the database session
    Returns:
        UserResponse -- the updated user 
    '''
    updated_data = await auth.update_user(db, user_id, update_req)
    return updated_data  # type: ignore


@auth_router.delete('/user/{user_id}/', response_model=ResponseMessage)
async def delete_user(
    user_id: int,
    db: DatabaseRequired,
    admin: AdminProtected
) -> ResponseMessage:
    '''Deletes a user given an existing user ID

    Arguments:
        user_id {int} -- the ID of the user to be deleted
        db {requires_db} -- a database session
        admin {admin_required} -- an admin user, ensures the Admin isn't deleting
        themselves
    Returns:
        ResponseMessage -- A message indicating the deletion was successful
    '''
    await auth.delete_user(db, user_id, admin.username)
    return ResponseMessage(message='User deleted')  # type: ignore


@auth_router.get('/user/{user_id}/', response_model=UserResponse)
async def read_user(
    user_id: int,
    db: DatabaseRequired,
    reader: CurrentUser
) -> UserResponse:
    '''Reads a user with 'no read up' i.e a user cannot read a user with a 
    higher role / permission
    
    
    Arguments:
        user_id {int} -- the id of the user to read
        db {requires_db} -- the database session
        reader {role_required} -- the "reader" or user making the request

    Raises:
        HTTPNotFound: The user does not exist
        HTTPForbidden: The user does not have permission to read the user

    Returns:
        UserResponse -- The user attempting to be read
    '''
    user = await auth.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')

    if not (reader.role >= user.role):
        raise HTTPForbidden('Cannot read a user with higher permissions')

    return user  # type: ignore


@auth_router.get('/all/', response_model=list[UserResponse])
async def public_read_all(
    db: DatabaseRequired,
    reader: CurrentUser
) -> list[UserResponse]:
    users = await auth.role_based_read_all(reader, db)
    return users  # type: ignore


@auth_router.get(
    '/user_details/',
    dependencies=[Depends(AdminRequired())],
    response_model=list[UserDetailsResponse]
)
async def read_all_details(db: DatabaseRequired) -> list[UserDetailsResponse]:
    '''Admin protected route to read all of the user details, including 
    the creation date and last updated timestamps

    Arguments:
        db {requires_db}

    Returns:
        list[UserDetailsResponse]
    '''
    users = await auth.get_all(db)
    return users  # type: ignore


@auth_router.get(
    '/read/{user_id}/',
    dependencies=[Depends(AdminRequired())],
    response_model=UserDetailsResponse
)
async def read_user_details(
    user_id: int,
    db: DatabaseRequired
) -> UserDetailsResponse:
    user = await auth.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')
    return user  # type: ignore
