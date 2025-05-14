import logging
from typing import Annotated

from fastapi import APIRouter, Body

from app.db.dependency import DatabaseDep

from app.common.errors import HTTPForbidden
from app.utils.openapi_extra.responses import ErrorDoc, AuthErrors

from app.api.users.service import UserService

from .errors import HTTPInvalidCredentials
from .dependency import SessionIdDep, FingerprintDep, SessionServiceDep
from .schema import (
    SessionResponse,
    SessionIdentity,
    SessionInfo,
    LogoutResponse,
    LoginBody,
)


auth_logger = logging.getLogger("security.auth")


auth_router = APIRouter()


@auth_router.post(
    "/login",
    response_model=SessionResponse,
    responses=ErrorDoc("When the user provides invalid credentials", 401),
)
async def login_user(
    auth_form: Annotated[LoginBody, Body(...)],
    session_service: SessionServiceDep,
    client: FingerprintDep,
    db: DatabaseDep,
) -> SessionResponse:
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
    user_service = UserService(db)
    verified_user = await user_service.authenticate(auth_form)
    if not verified_user:
        auth_logger.warning(f"Failed login attempt for user {auth_form.username}")
        raise HTTPInvalidCredentials()

    session_id = await session_service.assign_session(
        username=verified_user.username, role=str(verified_user.role), client=client
    )

    auth_logger.info(
        f"User {verified_user.username} logged in with role {verified_user.role}"
    )

    session_identity = SessionIdentity(
        username=verified_user.username, role=str(verified_user.role)
    )

    return SessionResponse(session_id=session_id, identity=session_identity)


@auth_router.post("/logout/", response_model=LogoutResponse, responses=AuthErrors())
async def logout_user(
    session_auth: SessionIdDep, session_service: SessionServiceDep
) -> LogoutResponse:
    """Logs out the user using the _"Session ID" dependency_

    - Load the clients signed api key from the clients cookies
    - Decrypts the api key in the Redis store,

    - if the session key hasn't been tampered with by the user and is valid the
    session is revoked by deleting the key in the Redis store mapped to the api key
    and the cookie is removed from the client
    Arguments:
        request {Request}  - the request to get the existing session ID from
    Raises:
        If the api_key is not found or was tampered with
        by the client
    Returns:
        LogoutResponse -- a message indicating the logout was successful
    """
    if not session_auth or not session_auth.credentials:
        raise HTTPForbidden("Invalid or expired session.")
    try:
        await session_service.revoke(session_auth.credentials)
    except Exception:
        pass

    auth_logger.info(f"User with API key {session_auth.credentials} logged out")

    return LogoutResponse()


@auth_router.get("/session/", response_model=SessionInfo, responses=AuthErrors())
async def get_session_status(
    session_auth: SessionIdDep, session_service: SessionServiceDep
) -> SessionInfo:
    """Returns the session information for the current user

    Args:
        session_auth (SessionIdDep): _the session id_
        session_service (SessionServiceDep): _the session service_

    Raises:
        HTTPForbidden: _invalid or expired session_

    Returns:
        SessionInfo: _the session data_
    """
    if not session_auth or not session_auth.credentials:
        raise HTTPForbidden("Invalid or expired Session")

    key_info = await session_service.get_session_health(
        signed_key=session_auth.credentials
    )

    if not key_info:
        raise HTTPForbidden("Invalid or expired Session.")

    return key_info
