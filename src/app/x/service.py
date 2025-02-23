from typing import Optional

from sqlalchemy import select
from app.common.errors import HTTPForbidden, HTTPNotFound
from app.auth.user_schema import CreateUserForm, UpdateUserForm, AuthForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.user import User
from app.security import crypto
from app.utils.crud_mixin import CRUDService


class AuthService(CRUDService[User]):
    '''The controller for the User ORM


    Arguments:
        CRUDService {_type_} 
    '''

    def __init__(self) -> None:
        super().__init__(User)

    async def authenticate(
        self,
        auth_form: AuthForm,
        db: AsyncSession
    ) -> Optional[User]:
        '''verifies the user credentials by checking the hashed password

        Arguments:
            auth_form {AuthForm} 
            db {AsyncSession}
        Returns:
            Optional[User] 
        '''
        existing_user = await self.get_username(auth_form.username, db)

        if not existing_user:
            return None

        if not crypto.check_password(
            auth_form.password,
            existing_user.password_hash
        ):
            return None

        return existing_user

    async def get_username(self, username: str, db: AsyncSession) -> Optional[User]:
        return await self.get_by(User.username == username, db)

    async def username_exists(self, db: AsyncSession, username: str) -> bool:
        '''checks if a username is already taken
        Arguments:
            db {AsyncSession} -- the database session
            username {str} -- the username to check
        Returns:
            bool -- True if the username is taken, False otherwise
        '''
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar() is not None

    async def create_user(self, db: AsyncSession, create_req: CreateUserForm) -> User:
        '''creates and inserts a user model using the create user request
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
        '''adds the key 'password_hash' to the request body 
        and deletes the key 'password' from the request body
        so the user ORM can be updated using the hashed passowrd 

        Arguments:
            schema {dict} -- pydantic model dump
        '''
        if not 'password' in req_model_dump:
            return

        plain_pwd = req_model_dump['password']
        req_model_dump['password_hash'] = crypto.hash_password(plain_pwd)
        del req_model_dump['password']

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        update_req: UpdateUserForm
    ) -> User:
        '''updates a user ORM model using the UpdateUser request 
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
            raise HTTPNotFound('User')

        update_dump = update_req.model_dump(exclude_unset=True)
        self.hash_password_in_req(update_dump)

        return await self.update(db, usr_updated, update_dump)

    async def delete_user(
        self,
        db: AsyncSession,
        user_id: int,
        admin_name: str
    ) -> None:
        '''deletes the user given a valid user_id 

        Arguments:
            db {AsyncSession} 
            user_id {int}  

        Raises:
            HTTPException: 404
        '''
        user = await self.get_by_id(user_id, db)
        if user is None:
            raise HTTPNotFound('User')
        acting_admin = await self.get_username(admin_name, db)
        if acting_admin is None or acting_admin.id == user_id:
            raise HTTPForbidden('You cannot delete yourself, why? Just why?')

        await self.delete_model(db, user)

    async def get_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        return await self.get_by(User.id == user_id, db)

    async def role_based_read_all(
        self,
        reader_role: User,
        db: AsyncSession
    ) -> Optional[list[User]]:
        '''
        returns all the users in the database if the user is an admin
        otherwise returns only the user's data 

        Arguments:
            user_role {str} -- the role of the user
            db {AsyncSession} -- the database session

        Returns:
            list[User] -- list of users
        '''

        stmnt = select(User).where(
            User.role_level <= reader_role.role_level
        )
        return await self.execute_statement(stmnt, db)
