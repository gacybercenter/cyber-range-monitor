from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from app.core.dependency import DatabaseDep
from app.core.schemas import AuthForm, GenericAPIResponse
from app.core.errors import HTTPUnauthorized

from app.extensions.openapi_extra import APITags

from app.users.service import UserService

from .dependency import (
    APIKeyCookieDep,
    ClientIdentityDep,
    KeyProviderDep
)


auth_router = APIRouter(
    prefix="/auth",
    tags=[APITags.auth]
)


@auth_router.post("/login/", response_class=JSONResponse)
async def login(
    auth_form: Annotated[AuthForm, Form(...)],
    key_provider: KeyProviderDep,
    client: ClientIdentityDep,
    db: DatabaseDep
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
    user_service = UserService(db)
    authenticated_user = await user_service.authenticate(auth_form)
    if not authenticated_user:
        raise HTTPUnauthorized("Invalid username or password")
    
    api_key = await key_provider.issue_key(
        username=authenticated_user.username,
        role=str(authenticated_user.role),
        client_identity=client
    )
    
    res_content = GenericAPIResponse(
        message="Login successful",
        data={"identity": api_key}
    ).serialize()
    
    cookie_options = key_provider.auth_cookie(api_key)    
    
    response = JSONResponse(content=res_content)
    response.set_cookie(**cookie_options)
    return response


@auth_router.post("/logout/", response_class=JSONResponse)
async def logout(
    api_key: APIKeyCookieDep,
    key_provider: KeyProviderDep
) -> JSONResponse:
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
    if not api_key:
        raise HTTPUnauthorized("Invalid session")
    response = JSONResponse(content={"message": "Logout successful"})
    try:
        await key_provider.revoke_key(api_key, response)
    except Exception:
        pass
    return response
    



