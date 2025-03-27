from typing import Annotated

from fastapi import APIRouter, Depends, Body, status

from app.core.schemas import APIListResponse, GenericAPIResponse
from app.core.types import PathID
from app.core.errors import HTTPBadRequest, HTTPForbidden, HTTPNotFound

from app.extensions.openapi_extra import APITags

from .errors import UserNotFound

from .dependency import (
    AdminRequired,
    CurrentUserDep,
    AdminRoleDep,
    UserServiceDep
)

from .schema import (
    CreateUserForm,
    UpdateUserForm,
    UserDetailsResponse,
    UserResponse
)


user_router = APIRouter(prefix="/users", tags=[APITags.user])


@user_router.get("/me/", response_model=UserResponse)
async def current_user(reader: CurrentUserDep) -> UserResponse:
    """Reads the current user

    Arguments:
        reader {CurrentUser} -- the reader

    Returns:
        UserResponse -- the current user
    """
    return UserResponse.to_model(reader)


@user_router.get("/", response_model=APIListResponse[UserResponse])
async def get_all_users(
    user_service: UserServiceDep,
    reader: CurrentUserDep
) -> APIListResponse[UserResponse]:
    """reads all users based on the role of the reader (no read up)
    Arguments:
        user_service {UserController} -- _the user controller_
        reader {CurrentUser} -- _the reader_

    Returns:
        list[UserResponse] -- _description_
    """
    user_models = await user_service.role_based_read_all(reader)
    if not user_models:
        raise UserNotFound()
    users = [UserResponse.to_model(user) for user in user_models]
    return APIListResponse.from_list(users)


@user_router.get(
    "/details",
    dependencies=[Depends(AdminRequired)],
    response_model=APIListResponse[UserDetailsResponse],
)
async def all_user_details(user_service: UserServiceDep) -> APIListResponse[UserDetailsResponse]:
    """Admin protected route to read all of the user details, including
    the creation date and last updated timestamps

    Arguments:
        db {requires_db}

    Returns:
        list[UserDetailsResponse]
    """
    users = await user_service.read_all()
    data = [UserDetailsResponse.to_model(user) for user in users]
    return APIListResponse.from_list(data)


@user_router.get(
    "/details/{user_id}/",
    dependencies=[Depends(AdminRequired)],
    response_model=UserDetailsResponse,
)
async def user_details(
    user_id: PathID, user_service: UserServiceDep
) -> UserDetailsResponse:
    """reads the details of an individual user

    Arguments:
        user_id {int} -- the id of the user to read
        db {DatabaseRequired} -- the database session

    Raises:
        HTTPNotFound: the user does not exist

    Returns:
        UserDetailsResponse -- the details of the individual user
    """

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPNotFound("User")
    return UserDetailsResponse.to_model(user)


@user_router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    create_req: Annotated[CreateUserForm, Body(...)],
    user_service: UserServiceDep
) -> UserResponse:
    """**[ADMIN]**
    Creates a user given valid form data and inserts
    the created user into the database and returns the
    created user

    _Arguments_:
        - create_schema {CreateUserForm} -- the form data
        - db {AsyncSession} - the database session
    _Raises_:
        HTTPException: 400 - Username is already taken
    _Returns_:
        UserResponse -- the created user
    """
    username_taken = await user_service.get_username(create_req.username)
    if username_taken:
        raise HTTPBadRequest("Username is already taken")

    resulting_user = await user_service.create_user(create_req)
    return UserResponse.to_model(resulting_user)


@user_router.patch(
    "/{user_id}/",
    response_model=UserResponse,
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_202_ACCEPTED
)
async def update_user(
    user_id: PathID,
    update_req: Annotated[UpdateUserForm, Body()],
    user_service: UserServiceDep
) -> UserResponse:
    """updates the user given an id and uses the schema to update the user's data

    Arguments:
        user_id {int} -- user id of the user to update
        update_schema {UpdateUser} -- the request body schema
        db {AsyncSession} -- the database session
    Returns:
        UserResponse -- the updated user
    """
    updated_data = await user_service.update_user(user_id, update_req)
    return UserResponse.to_model(updated_data)


@user_router.delete("/{user_id}/", response_model=GenericAPIResponse)
async def delete_user(
    user_id: PathID, user_controller: UserServiceDep, admin: AdminRoleDep
) -> GenericAPIResponse:
    """Deletes a user given an existing user ID

    Arguments:
        user_id {int} -- the ID of the user to be deleted
        db {requires_db} -- a database session
        admin {admin_required} -- an admin user, ensures the Admin isn't deleting
        themselves
    Returns:
        ResponseMessage -- A message indicating the deletion was successful
    """
    await user_controller.delete_user(user_id, admin.username)
    return GenericAPIResponse(message="User deleted", data={"user_id": user_id})


@user_router.get("/{user_id}/", response_model=UserResponse)
async def read_user(
    user_id: PathID, user_service: UserServiceDep, reader: CurrentUserDep
) -> UserResponse:
    """Reads a user with 'no read up' i.e a user cannot read a user with a
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
    """
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPNotFound("User")

    if not (reader.role >= user.role):
        raise HTTPForbidden("Cannot read a user with higher permissions")

    return UserResponse.to_model(user)
