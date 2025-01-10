from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from api.main.schemas.user import CreateUser, UpdateUser, LoginRequest
from api.db.service_wrapper import CRUDService
from api.models.user import User
from api.utils.security.hashing import hash_pwd, check_pwd


class UserService(CRUDService[User]):
    '''
    Manages the ORM CRUD operations for the user model 

    Arguments:
        CRUDService{User} -- Inherits from the CRUDService Wrapper 
        specifying 'User' as the ORM model 
    '''

    def __init__(self) -> None:
        super().__init__(User)

    async def username_is_taken(self, db: AsyncSession, username: str) -> bool:
        '''
        checks if a username is already taken
        Arguments:
            db {AsyncSession} -- the database session
            username {str} -- the username to check
        Returns:
            bool -- True if the username is taken, False otherwise
        '''
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar() is not None

    async def create_user(self, db: AsyncSession, create_req: CreateUser) -> User:
        '''
        creates and inserts a user model using the create user request
        schema 

        Arguments:
            db {AsyncSession} -- the database session
            create_req {CreateUser} -- the request schema

        Returns:
            User -- the created user 
        '''
        user_in = create_req.model_dump()
        self.hash_password_in_req(user_in)
        return await self.create(db, user_in)

    def hash_password_in_req(self, req_model_dump: dict) -> None:
        '''
        adds the key 'password_hash' to the request body 
        and deletes the key 'password' from the request body
        so the user ORM can be updated using the hashed passowrd 

        Arguments:
            schema {dict} -- pydantic model dump
        '''
        if not 'password' in req_model_dump:
            return

        plain_pwd = req_model_dump['password']
        req_model_dump['password_hash'] = hash_pwd(plain_pwd)
        del req_model_dump['password']

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        update_req: UpdateUser
    ) -> User:
        '''
        updates a user ORM model using the UpdateUser request 
        body schema given a valid user_id 

        Arguments:
            db {AsyncSession}
            user_id {int} 
            update_req {UpdateUser} 
        Raises:
            HTTPException: 404
        Returns:
            User -- the updated user ORM model
        '''
        usr_updated = await self.get_by_id(user_id, db)
        if not usr_updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        update_dump = update_req.model_dump(exclude_unset=True)
        self.hash_password_in_req(update_dump)

        return await self.update(db, usr_updated, update_dump)

    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
        '''
        deletes the user given a valid user_id 

        Arguments:
            db {AsyncSession} 
            user_id {int}  

        Raises:
            HTTPException: 404
        '''
        user = await self.get_by_id(user_id, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        await self.delete_model(db, user)

    async def get_by_id(
        self,
        user_id: int,
        db: AsyncSession
    ) -> Optional[User]:
        return await self.get_by(User.id == user_id, db)

    async def verify_credentials(
        self,
        login_req: LoginRequest,
        db: AsyncSession
    ) -> Optional[User]:
    
        existing_user = await self.get_by(
            User.username == login_req.username,
            db
        )
        if not existing_user:
            return None
        
        if not check_pwd(login_req.password, existing_user.password_hash):
            return None 
        
        return existing_user 
