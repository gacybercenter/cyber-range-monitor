from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from api.main.schemas.user import CreateUser, UpdateUser, LoginRequest
from api.db.crud import CRUDService
from api.models.user import User, UserRoles
from api.utils.security.hashing import hash_pwd, check_pwd
from api.utils.errors import ResourceNotFound


class UserService(CRUDService[User]):
    '''
    Manages the ORM operations for the user model 

    Arguments:
        CRUDService{User} -- Inherits from the CRUDService Wrapper 
        specifying 'User' as the ORM model in the constructor  
    '''

    def __init__(self) -> None:
        super().__init__(User)

    async def username_exists(self, db: AsyncSession, username: str) -> bool:
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
            raise ResourceNotFound('User')

        update_dump = update_req.model_dump(exclude_unset=True)
        self.hash_password_in_req(update_dump)

        return await self.update(db, usr_updated, update_dump)

    async def delete_user(self, db: AsyncSession, user_id: int, admin_name: str) -> None:
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
            raise ResourceNotFound(
                'User')
        acting_admin = await self.get_username(admin_name, db)
        if acting_admin is None or acting_admin.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You cannot delete yourself, why? Just why?'
            )
            
        await self.delete_model(db, user)

    async def get_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        return await self.get_by(User.id == user_id, db)

    
    async def role_based_read_all(
        self,
        reader_role: str,
        db: AsyncSession
    ) -> list[User]:
        '''
        returns all the users in the database if the user is an admin
        otherwise returns only the user's data 

        Arguments:
            user_role {str} -- the role of the user
            db {AsyncSession} -- the database session

        Returns:
            list[User] -- list of users
        '''
        all_users = await self.get_all(db)
        if reader_role == UserRoles.admin.value:
            return all_users 
        
        resolved_reader = UserRoles(reader_role)
        return [user for user in all_users 
            if resolved_reader >= UserRoles(user.role)
        ]      
            
            
            
        
        
        
        
            
            
        
        
        
        
        
        
        
        
        
        
    
    async def verify_credentials(
        self,
        form_username: str,
        form_password: str,
        db: AsyncSession
    ) -> Optional[User]:

        existing_user = await self.get_username(form_username, db)

        if not existing_user:
            return None

        if not check_pwd(form_password, existing_user.password_hash):  # type: ignore
            return None

        return existing_user

    async def get_username(self, username: str, db: AsyncSession) -> Optional[User]:
        return await self.get_by(User.username == username, db)
