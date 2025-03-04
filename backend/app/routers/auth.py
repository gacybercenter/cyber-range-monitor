from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse

from app.auth import session_service
from app.auth.dependency import SESSION_COOKIE_BEARER, RequireClientIdentity
from app.schemas.base import AuthForm
from app.shared.errors import HTTPUnauthorized
from app.users.dependency import UserController

auth_router = APIRouter(prefix="/auth", tags=["Authentication & Authorization"])


@auth_router.post("/login/", response_class=JSONResponse)
async def login(
    auth_form: Annotated[AuthForm, Form(...)],
    client: RequireClientIdentity,
    user_service: UserController,
) -> JSONResponse:
    """Checks the credentials provided by the 'AuthForm'
    and in the response sets a cookie with the session id when given
    valid login credentials.

    Arguments:
        auth_form {AuthForm} -- Has types to enforce constraints on the request body
        client {RequireClientIdentity} -- The client identity
        user_service {UserController} -- The user controller
    Raises:
        HTTPUnauthorized: 401 - If the user is not authenticated
    Returns:
        Response
    """

    authenticated_user = await user_service.authenticate(auth_form)
    if not authenticated_user:
        raise HTTPUnauthorized("Invalid username or password")

    session_cookie_kwargs = await session_service.create_session_cookie(
        username=authenticated_user.username,
        role=str(authenticated_user.role),
        client_identity=client,
    )
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(**session_cookie_kwargs)

    return response


@auth_router.post("/logout", dependencies=[Depends(SESSION_COOKIE_BEARER)])
async def logout(request: Request) -> JSONResponse:
    """[AUTH] - Logs out the user using the "SessionAuth" (SessionAuthority)
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
    """
    response = JSONResponse(content={"message": "Logout successful"})
    session_signature = await session_service.get_session_cookie(request)
    if not session_signature:
        raise HTTPUnauthorized("Invalid session")
    try:
        await session_service.revoke_session(session_signature, response)
    except Exception:
        pass
    return response
