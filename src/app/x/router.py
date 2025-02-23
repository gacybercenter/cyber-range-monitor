from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse


from app.config import running_config
from app.common.errors import HTTPUnauthorized
from app.auth.user_schema import AuthForm
from app.services.auth import AuthService, SessionService
from app.common.dependencies import (
    SessionAuth,
    DatabaseRequired,
    IdentityRequired
)
from app.auth.sessions.schemas import SessionData


settings = running_config()


auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
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
async def logout(request: Request) -> JSONResponse:
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
