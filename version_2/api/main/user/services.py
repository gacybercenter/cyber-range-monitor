from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from api.main.user.schemas import CreateUser, UpdateUser
from api.db.mixins import CRUDService
from api.models.user import User, UserRoles
from api.utils.security import HashManager


class UserService(CRUDService[User]):
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
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar() is not None
    
    async def create_user(
        self, 
        db: AsyncSession, 
        create_schema: CreateUser
    ) -> User:
        user_in = create_schema.model_dump()
        self.hash_password_in_schema(user_in)
        return await self.create(db, user_in) # type: ignore

    
    def hash_password_in_schema(self, schema: dict) -> None:
        '''
        adds the key 'password_hash' to the schema and hashes 
        the plaintext password 

        Arguments:
            schema {dict} -- pydantic model dump
        '''
        if not 'password' in schema:
            return 
        plain_pwd = schema['password']
        schema['password_hash'] = HashManager.hash_str(plain_pwd)
        del schema['password']
        

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        update_schema: UpdateUser
    ) -> User:
        usr_updated = await self.get_by_id(user_id, db)
        if not usr_updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        update_dump = update_schema.model_dump(exclude_unset=True)
        self.hash_password_in_schema(update_dump)
        return await self.update(db, usr_updated, update_dump)
    
    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
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
    
    
    async def is_authenticated(self) -> bool:
        return True # TODO
    

    
    
        
        
        
        
        
        
        
        
        
        
    
    


