from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.user_schema import CreateUser, UpdateUser
from app.services.mixins import CRUDService
from app.models.user import User, UserRoles
from app.core.security.hashing import hash_pwd, check_pwd
from app.common.errors import HTTPNotFound, HTTPForbidden


class UserService(CRUDService[User]):
    '''
    Manages the ORM operations for the user model 

    Arguments:
        CRUDService{User} -- Inherits from the CRUDService Wrapper 
        specifying 'User' as the ORM model in the constructor  
    '''

    def __init__(self) -> None:
        super().__init__(User)

    async def get_username(self, username: str, db: AsyncSession) -> Optional[User]:
        return await self.get_by(User.username == username, db)

    
    
    
    
    
    
    
    