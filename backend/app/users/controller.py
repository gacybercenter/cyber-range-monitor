
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions.security import crypto
from app.models import User
from app.shared.crud_mixin import CRUDService

from .errors import DeleteSelfForbidden, UserNotFound
from .schemas import AuthForm, CreateUserForm, UpdateUserForm


class UserService(CRUDService[User]):
    """The controller for the User ORM"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User)
        self.db = db

    async def authenticate(self, auth_form: AuthForm) -> User | None:
        """verifies the user credentials by checking the hashed password

        Arguments:
            auth_form {AuthForm}
            db {AsyncSession}
        Returns:
            Optional[User]
        """
        existing_user = await self.get_username(auth_form.username)

        if not existing_user:
            return None

        if not crypto.check_password(auth_form.password, existing_user.password_hash):
            return None

        return existing_user

    async def get_username(self, username: str) -> User | None:
        return await self.get_by(User.username == username, self.db)

    async def require_username(self, username: str) -> User:
        user = await self.get_username(username)
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
        return await self.create(self.db, user_in)

    def hash_password_in_req(self, req_model_dump: dict) -> None:
        """adds the key 'password_hash' to the request body
        and deletes the key 'password' from the request body
        so the user ORM can be updated using the hashed passowrd

        Arguments:
            schema {dict} -- pydantic model dump
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
            db {AsyncSession}
            user_id {int}
            update_req {UpdateUser}
        Raises:
            HTTPException: 404
        Returns:
            User -- the updated user ORM model
        """
        usr_updated = await self.get_by_id(user_id)
        if not usr_updated:
            raise UserNotFound()

        update_dump = update_req.model_dump(exclude_unset=True)
        self.hash_password_in_req(update_dump)

        return await self.update(self.db, usr_updated, update_dump)

    async def delete_user(self, user_id: int, admin_name: str) -> None:
        """deletes the user given a valid user_id

        Arguments:
            db {AsyncSession}
            user_id {int}

        Raises:
            HTTPException: 404
        """
        user = await self.get_by_id(user_id)
        if user is None:
            raise UserNotFound()
        acting_admin = await self.get_username(admin_name)
        if acting_admin is None or acting_admin.id == user_id:
            raise DeleteSelfForbidden()

        await self.delete_model(self.db, user)

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.get_by(User.id == user_id, self.db)

    async def role_based_read_all(self, reader_role: User) -> list[User] | None:
        """
        returns all the users in the database if the user is an admin
        otherwise returns only the user's data

        Arguments:
            user_role {str} -- the role of the user
            db {AsyncSession} -- the database session

        Returns:
            list[User] -- list of users
        """

        stmnt = select(User).where(User.role_level <= reader_role.role_level)
        return await self.execute_statement(stmnt, self.db)

    async def read_all(self) -> list[User]:
        """returns all the users in the database
        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            list[User] -- list of users
        """
        return await self.get_all(self.db)


async def get_user_service(db: AsyncSession) -> UserService:
    return UserService(db)
