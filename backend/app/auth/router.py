import logging
from typing import Annotated

from fastapi import APIRouter, Body, status

from app.core.dependency import DatabaseDep
from app.core.schemas import AuthForm

from app.extensions.openapi_extra import APITags

from app.users.service import UserService

from app.core.errors import HTTPForbidden

from .dependency import (
    KeyBearerSecurity,
    ClientIdentityDep,
    KeyServiceDep,
    HTTPInvalidCredentials
)
from .schemas import (
    APIKeyResponse, KeyBearerIdentity, LogoutResponse
)

from app.extensions.openapi_extra import err_response_doc, AUTH_DEP_RESPONSES

auth_logger = logging.getLogger("auth")


auth_router = APIRouter(
    prefix="/auth",
    tags=[APITags.auth]
)


@auth_router.post("/",  response_model=APIKeyResponse, responses={
    status.HTTP_401_UNAUTHORIZED: err_response_doc(
        'When the user provides invalid credentials'
    )
})
async def login_user(
    auth_form: Annotated[AuthForm, Body(...)],
    key_provider: KeyServiceDep,
    client: ClientIdentityDep,
    db: DatabaseDep
) -> APIKeyResponse:
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
    authenticated_user = await user_service.authenticate(auth_form)
    if not authenticated_user:
        auth_logger.warning(
            f"Failed login attempt for user {auth_form.username}")
        raise HTTPInvalidCredentials()

    api_key = await key_provider.assign_key(
        username=authenticated_user.username,
        role=str(authenticated_user.role),
        client_identity=client
    )
    auth_logger.info(
        f"User {authenticated_user.username} logged in with role {authenticated_user.role}")
    return APIKeyResponse(
        api_key=api_key,
        identity=KeyBearerIdentity(
            username=authenticated_user.username,
            role=str(authenticated_user.role)
        )
    )


@auth_router.post("/logout/", response_model=LogoutResponse, responses=AUTH_DEP_RESPONSES)
async def logout_user(
    key: KeyBearerSecurity,
    key_provider: KeyServiceDep
) -> LogoutResponse:
    """Logs out the user using the _"api_key" dependency_

    - Load the clients signed api key from the clients cookies
    - Decrypts the api key in the Redis store,

    - if the key hasn't been tampered with by the user and is valid the
    session is revoked by deleting the key in the Redis store mapped to the api key 
    and the cookie is removed from the client
    Arguments:
        request {Request}  - the request to get the existing session ID from
    Raises:
        If the api_key is not found or was tampered with
        by the client
    Returns:
        JSONResponse -- a message indicating the logout was successful
    """
    if not key or not key.credentials:
        raise HTTPForbidden("Invalid or missing API key")
    try:
        await key_provider.revoke(key.credentials)
    except Exception:
        pass

    auth_logger.info(f"User with API key {key.credentials} logged out")
    return LogoutResponse()
