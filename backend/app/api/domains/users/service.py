from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions.http import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPNotFound,
    HTTPUnauthorized,
)
from app.api.schemas.users import (
    DetailedUser,
    DetailedUserPage,
    PublicUserUpdateModel,
    UserCreateModel,
    UserModel,
    UserPage,
    UserQueryParams,
)
from app.infrastructure.security.passwords import PasswordManager
from app.infrastructure.security.roles import Role

from .repo import UserReadMode, UserRepository


class UserService:
    """The service for the User model"""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def authenticate(self, username: str, plain_password: str) -> UserModel:
        existing_user = await self.repo.get_by_username(
            username, user_read=UserReadMode.COMPLETE
        )
        if not existing_user:
            raise HTTPUnauthorized('Invalid credentials')

        passwords = PasswordManager()
        if not passwords.check_password(
            plain_password=plain_password,
            stored_hash=existing_user.password_hash
        ):
            raise HTTPUnauthorized('Invalid credentials')

        return UserModel.convert(existing_user)

    async def get_user(self, user_id: str, reader_role: Role) -> UserModel:
        user = await self.repo.get_by_id(user_id, user_read=UserReadMode.DEFAULT)
        if not user:
            raise HTTPNotFound(resource_name='user')

        if reader_role < user.role:
            raise HTTPForbidden('You do not have permission to read this user')

        return UserModel.convert(user)

    async def get_detailed_user(self, user_id: str) -> DetailedUser:
        user = await self.repo.get_by_id(user_id, user_read=UserReadMode.DETAILED)
        if not user:
            raise HTTPNotFound(resource_name='user')
        return DetailedUser.convert(user)

    def _prepare_user_request(
        self,
        req: PublicUserUpdateModel | UserCreateModel,
    ) -> dict:
        """Prepares the user request for updating or creating a user"""
        user_data = req.dump_exclude(exclude={'password'})

        if req.password:
            passwords = PasswordManager()
            user_data['password_hash'] = passwords.hash_password(req.password)
        return user_data

    async def create_user(self, create_req: UserCreateModel) -> UserModel:
        if await self.repo.username_exists(create_req.username):
            raise HTTPBadRequest('Username already taken')

        user_in = self._prepare_user_request(create_req)
        new_user = await self.repo.create(user_in)
        return UserModel.convert(new_user)

    async def new_username_taken(
        self, new_username: str | None, old_username: str
    ) -> bool:
        """Checks if the new username is already taken"""
        return (
            new_username is not None
            and new_username != old_username
            and await self.repo.username_exists(new_username)
        )

    async def update_user(
        self,
        user_id: str,
        update_req: PublicUserUpdateModel,
        reader_role: Role,
    ) -> UserModel:
        usr_updated = await self.repo.get_by_id(
            user_id, user_read=UserReadMode.DETAILED
        )
        if not usr_updated:
            raise HTTPNotFound(resource_name='user')

        if reader_role != Role.ADMIN and user_id != usr_updated.id:
            raise HTTPBadRequest('You can only update your own user')

        if await self.new_username_taken(
            new_username=update_req.username, old_username=usr_updated.username
        ):
            raise HTTPBadRequest('Username already taken')

        user_in = self._prepare_user_request(update_req)
        user_out = await self.repo.update(
            usr_updated,
            user_in,
        )

        return UserModel.convert(user_out)

    async def delete_user(self, user_id: str, admin_name: str) -> None:
        existing_user = await self.repo.get_by_id(
            user_id=user_id,
            user_read=UserReadMode.COMPLETE,
        )
        if not existing_user:
            raise HTTPNotFound(resource_name='user')

        if existing_user.username == admin_name:
            raise HTTPForbidden('An admin cannot delete themselves')

        if not await self.repo.delete(existing_user):
            raise HTTPBadRequest('Failed to delete user')

    async def get_user_page(
        self, params: UserQueryParams, reader_role: Role
    ) -> UserPage:
        """Gets a paginated list of users based on query parameters"""
        page_result = await self.repo.paginate_users(
            read_mode=UserReadMode.DEFAULT,
            options=params,
            reader_role=reader_role,
        )
        models = [UserModel.convert(user) for user in page_result['models']]

        return UserPage.create(
            data=models,
            page=page_result['page'],
            page_size=page_result['page_size'],
            total=page_result['total'],
        )

    async def get_detailed_user_page(self, params: UserQueryParams) -> DetailedUserPage:
        """Gets a paginated list of detailed users based on query parameters"""
        page_result = await self.repo.paginate_users(
            read_mode=UserReadMode.DETAILED, options=params, reader_role=Role.ADMIN
        )
        models = [DetailedUser.convert(user) for user in page_result['models']]
        return DetailedUserPage.create(
            data=models,
            page=page_result['page'],
            page_size=page_result['page_size'],
            total=page_result['total'],
        )

    async def get_current_user(self, user_id: str) -> UserModel:
        """Gets the current user by their ID"""
        user = await self.repo.get_by_id(
            user_id=user_id,
            user_read=UserReadMode.DEFAULT
        )
        if not user:
            raise HTTPNotFound(resource_name='user')
        return UserModel.convert(user)
