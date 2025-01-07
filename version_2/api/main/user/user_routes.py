from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.schemas.user_schema import CreateUser, UpdateUser, ReadUser, VerboseReadUser
from api.main.user.services import UserService
from api.db.main import get_db


user_router = APIRouter(
    prefix='/user',
    tags=['User']
)

user_service = UserService()


'''
routes todo

/register: [post] creates a new user 
/{user_id}: [get] gets a user
/{user_id}: [put] updates a user
/{user_id}: [delete] deletes a user

/: [get] gets all users
'''


@user_router.post('/register', response_model=ReadUser, status_code=status.HTTP_201_CREATED)
async def register_user(
    create_schema: CreateUser,
    db: AsyncSession = Depends(get_db)
) -> ReadUser:
    username_taken = await user_service.username_is_taken(db, create_schema.username)
    if username_taken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username is already taken'
        )
        
    resulting_user = await user_service.create_user(db, create_schema)
    return resulting_user # type: ignore
    

@user_router.put('/{user_id}', response_model=ReadUser, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    update_schema: UpdateUser,
    db: AsyncSession = Depends(get_db)
) -> ReadUser:
    
    updated_data = await user_service.update_user(db, user_id, update_schema)  
    return updated_data # type: ignore

@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    if not await user_service.is_authenticated():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized'
        )
    await user_service.delete_user(db, user_id)

@user_router.get('/{user_id}', response_model=ReadUser, status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)) -> ReadUser:
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user # type: ignore

@user_router.get('/', response_model=list[ReadUser])
async def read_all_users(db: AsyncSession = Depends(get_db)) -> list[ReadUser]:
    users = await user_service.get_all(db)
    return [ReadUser.model_validate(user) for user in users]

@user_router.get('/profile/{user_id}', response_model=VerboseReadUser, status_code=status.HTTP_200_OK)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)) -> VerboseReadUser:
    '''
    Get user profile by id in the query param (e.g /user/profile?id=1)
    and returns detailed information about the user 

    Keyword Arguments:
        id {int} -- user id
        db {AsyncSession} --  (default: {Depends(get_db)})

    Raises:
        HTTPException: 
    Returns:
        VerboseReadUser -- user with all attributes
    '''
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user # type: ignore 
    







