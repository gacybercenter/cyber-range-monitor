from app.core.schemas import CustomBaseModel, APIRequestModel
from pydantic import Field
from app.core.types import FixedStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import crypto

from app.core.interfaces import DatabaseService

from app.core.errors import HTTPBadRequest
from app.db.models import User


from .errors import DeleteSelfForbidden, UserNotFound, UsernameTaken
from .schema import AuthForm, CreateUserForm, UpdateUserForm, UserResponse


class UserService(DatabaseService[User]):
    """The service for the User model"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)


    def serialize(self, model: User) -> UserResponse:
        '''returns a UserResponse model from the User model

        Arguments:
            model {User} -- the databas model

        Returns:
            UserResponse -- the pydantic model
        '''
        return UserResponse.to_model(model)

    async def authenticate(self, auth_form: AuthForm) -> User | None:
        """verifies the user credentials by checking the hashed password

        Arguments:
            auth_form {AuthForm}
            db {AsyncSession}
        Returns:
            Optional[User]
        """
        existing_user = await self.by_username(auth_form.username)

        if not existing_user:
            return None

        correct_password = crypto.check_password(
            auth_form.password,
            existing_user.password_hash
        )

        if not correct_password:
            return None

        return existing_user

    async def by_username(self, username: str) -> User | None:
        return await self.models.get_by(User.username == username)

    async def require_username(self, username: str) -> User:
        '''gets the username and throws a 404 if not found
        
        Arguments:
            username {str} -- the username to search for
        Raises:
            HTTPException: 404 (UserNotFound)
        Returns:
            User -- the user model
        '''
        user = await self.by_username(username)
        if not user:
            raise UserNotFound()
        return user

    async def create_user(self, create_req: CreateUserForm) -> User:
        """creates and inserts a user model using the create user request
        schema

        Arguments:
            db {AsyncSession} -- the database session
            create_req {CreateUser} -- the request schema

        Returns:
            User -- the created user
        """
        user_in = create_req.model_dump()
        self.hash_password_in_req(user_in)
        return await self.models.create(user_in)

    def hash_password_in_req(self, req_model_dump: dict) -> None:
        """adds the key 'password_hash' to the request body
        and deletes the key 'password' from the request body
        so the user ORM can be updated using the hashed passowrd

        Arguments:
            req_model_dump {dict} -- pydantic model dump
        """
        if "password" not in req_model_dump:
            return

        plain_pwd = req_model_dump["password"]
        req_model_dump["password_hash"] = crypto.hash_password(plain_pwd)
        del req_model_dump["password"]

    async def update_user(self, user_id: int, update_req: UpdateUserForm) -> User:
        """updates a user ORM model using the UpdateUser request
        body schema given a valid user_id

        Arguments:
            user_id {int}
            update_req {UpdateUser}
        Raises:
            HTTPException: 404 (UserNotFound)
        Returns:
            User -- the updated user ORM model
        """
        usr_updated = await self.get_by_id(user_id)
        if not usr_updated:
            raise UserNotFound()

        update_dump = update_req.serialize()
        if not update_dump:
            raise HTTPBadRequest(
                'Cannot update a user without making any changes.'
            )

        self.hash_password_in_req(update_dump)
        # edge case where the user tries to update to a taken username
        if self.new_username_taken(update_req.username, usr_updated.username):
            raise UsernameTaken()

        return await self.models.update(usr_updated, update_dump)

    async def new_username_taken(
        self,
        new_username: str | None,
        old_username: str
    ) -> bool:
        """checks if the username is already taken

        Arguments:
            username {str} -- the username to check

        Returns:
            bool -- True if the username is already taken
        """
        return (
            new_username is not None and
            new_username != old_username and
            await self.by_username(new_username) is not None
        )

    async def delete_user(self, user_id: int, admin_name: str) -> None:
        """deletes the user given a valid user_id

        Arguments:
            user_id {int}
            admin_name {str} -- the name of the admin
        Raises:
            HTTPException: 404
        """
        user = await self.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        acting_admin = await self.by_username(admin_name)

        if acting_admin is None or acting_admin.id == user_id:
            raise DeleteSelfForbidden()

        await self.models.delete(user)

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.models.get_by(User.id == user_id)

    async def role_based_read_all(self, reader_role: User) -> list[User] | None:
        """
        returns all the users in the database if the user is an admin
        otherwise returns only the user's data

        Arguments:
            user_role {str} -- the role of the user

        Returns:
            list[User] -- list of users
        """
        stmnt = select(User).where(User.role_level <= reader_role.role_level)
        return await self.models.execute_on_all(stmnt)

    async def read_all_users(self) -> list[User]:
        """returns all the users in the database
        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            list[User] -- list of users
        """
        return await self.models.get_all()
