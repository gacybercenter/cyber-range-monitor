

from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse

from app.users.dependencies import UserController
from app.users.schemas import AuthForm
from .errors import HTTPInvalidCredentials
from .service import SessionService
from .schemas import ClientIdentity, SessionData
from .constant import SESSION_AUTHORITY, SESSION_CONFIG 

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
)

session_service = SessionService()


@auth_router.post('/login/')
async def login(
    request: Request,
    auth_form: Annotated[AuthForm, Form(...)],
    user_service: UserController
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
    
    authenticated_user = await user_service.authenticate(auth_form)
    if not authenticated_user:
        raise HTTPInvalidCredentials()
    
    client_identity = ClientIdentity.create(request)
    session_data = SessionData.create(
        username=authenticated_user.username,
        role=authenticated_user.role,
        client_identity=client_identity
    )
    signature = await session_service.create(session_data)
    response = JSONResponse({'message': 'Successfully logged in'})
    
    response.set_cookie(
        **SESSION_CONFIG.cookie_kwargs(signature)   
    )
    return response 

@auth_router.post('/logout/', dependencies=[Depends(SESSION_AUTHORITY)])
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
    response = JSONResponse({'message': 'Successfully logged out'})
    try:
        signature = request.cookies.get(SESSION_CONFIG.SESSION_COOKIE)
        await SESSION_AUTHORITY.revokes(signature, response)
    except Exception:
        pass
    return response
    
    
    
    
