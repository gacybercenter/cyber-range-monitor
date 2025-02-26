from typing import Annotated
from fastapi import APIRouter, Body, Depends, Form, status


from app.shared.errors import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from app.users.schemas import (
    CreateUserForm,
    UpdateUserForm,
    UserDetailsResponse,
    UserResponse
)
from app.users.dependency import AdminRequired, UserController, AdminProtected, CurrentUser
from app.shared.schemas import ResponseMessage

# =========================================
#           User Router
# =========================================

user_router = APIRouter(
    prefix='/user',
    tags=['Users']
)



@user_router.post(
    '/create/',
    response_model=UserResponse,
    dependencies=[Depends(AdminProtected)],
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    create_req: Annotated[CreateUserForm, Form(...)],
    user_service: UserController,
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
    username_taken = await user_service.get_username(create_req.username)
    if username_taken:
        raise HTTPBadRequest('Username is already taken')

    resulting_user = await user_service.create_user(create_req)
    return resulting_user  # type: ignore


@user_router.put(
    '/update/{user_id}/',
    response_model=UserResponse,
    dependencies=[Depends(AdminProtected)],
    status_code=status.HTTP_202_ACCEPTED
)
async def update_user(
    user_id: int,
    update_req: Annotated[UpdateUserForm, Body()],
    user_service: UserController
) -> UserResponse:
    '''updates the user given an id and uses the schema to update the user's data

    Arguments:
        user_id {int} -- user id of the user to update
        update_schema {UpdateUser} -- the request body schema
        db {AsyncSession} -- the database session
    Returns:
        UserResponse -- the updated user 
    '''
    updated_data = await user_service.update_user(user_id, update_req)
    return updated_data  # type: ignore


@user_router.delete('/del/{user_id}/', response_model=ResponseMessage)
async def delete_user(
    user_id: int,
    user_controller: UserController,
    admin: AdminRequired
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
    await user_controller.delete_user(user_id, admin.username)
    return ResponseMessage(message='User deleted')  # type: ignore


@user_router.get('/read/{user_id}/', response_model=UserResponse)
async def read_user(
    user_id: int,
    user_service: UserController,
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
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPNotFound('User')

    if not (reader.role >= user.role):
        raise HTTPForbidden('Cannot read a user with higher permissions')

    return user  # type: ignore


@user_router.get('/all/', response_model=list[UserResponse])
async def public_read_all(
    user_service: UserController,
    reader: CurrentUser
) -> list[UserResponse]:
    users = await user_service.role_based_read_all(reader)
    return users  # type: ignore


@user_router.get(
    '/all/details/',
    dependencies=[Depends(AdminProtected)],
    response_model=list[UserDetailsResponse]
)
async def read_all_details(
    user_service: UserController
) -> list[UserDetailsResponse]:
    '''Admin protected route to read all of the user details, including 
    the creation date and last updated timestamps

    Arguments:
        db {requires_db}

    Returns:
        list[UserDetailsResponse]
    '''
    users = await user_service.read_all()
    return users  # type: ignore


@user_router.get(
    '/details/{user_id}/',
    dependencies=[Depends(AdminProtected)],
    response_model=UserDetailsResponse
)
async def read_user_details(
    user_id: int,
    user_service: UserController
) -> UserDetailsResponse:
    '''reads the details of an individual user

    Arguments:
        user_id {int} -- the id of the user to read
        db {DatabaseRequired} -- the database session

    Raises:
        HTTPNotFound: the user does not exist

    Returns:
        UserDetailsResponse -- the details of the individual user
    '''

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPNotFound('User')
    return user  # type: ignore
