import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.errors import (
    ConflictError,
    ForbiddenError,
    ResourceNotFound,
    UnauthorizedAccess,
)
from range_monitor.infra.security._crypto import CryptoService
from range_monitor.schema.params import PageParams
from range_monitor.users.repo import UserRepository
from range_monitor.users.schema import (
    InternalUser,
    UserCreateBody,
    UserPage,
    UserPatchBody,
    UserPatchProfile,
    UserQuery,
    UserSchema,
)


class UsersService:
    def __init__(self, db: AsyncSession, crypto_service: CryptoService) -> None:
        self.users = UserRepository(db)
        self.crypto_service = crypto_service

    async def create_user(self, body: UserCreateBody, creator_id: str) -> UserSchema:
        '''
        Creates a new user in the system.

        Parameters
        ----------
        body : UserCreateBody
        creator_id : str
            The ID of the user creating this new user.

        Returns
        -------
        UserSchema

        Raises
        ------
        UnauthorizedAccess
            If the creator_id does not correspond to a
            valid user.
        ConflictError
            If the username is already taken.
        '''
        creator = uuid.UUID(creator_id)
        if not await self.users.get_internal_user(user_id=creator):
            raise UnauthorizedAccess('invalid_creator')


        if not await self.users.is_username_unique(body.username):
            raise ConflictError('username_taken')

        new_user = await self.users.create(
            username=body.username,
            password_hash=self.crypto_service.hash_password(body.password),
            role=body.role,
            created_by=creator
        )

        return UserSchema.convert(new_user)

    async def edit_user(
        self,
        user_id: str | uuid.UUID,
        params: UserPatchBody | UserPatchProfile
    ) -> UserSchema:
        '''
        Updates an existing user's details.

        Parameters
        ----------
        user_id : str | uuid.UUID
        params : UserPatchBody | UserPatchProfile

        Returns
        -------
        UserSchema

        Raises
        ------
        ResourceNotFound
            If the user_id does not correspond to an existing user.
        ConflictError
            If the new username is already taken by another user.
        '''
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        if not (existing := await self.users.get_user(user_id)):
            raise ResourceNotFound('user')

        if params.username and not await self.users.is_username_unique(
            params.username,
            excluding_id=user_id
        ):
            raise ConflictError('username_taken')

        patch = params.model_dump(exclude_unset=True)

        if password := patch.pop('password', None):
            patch['password_hash'] = self.crypto_service.hash_password(password)

        await self.users.edit_user(existing, patch)
        return UserSchema.convert(existing)

    async def delete_user_id(self, user_id: uuid.UUID, current_user_id: str) -> None:
        '''
        Deletes a user from the system.

        Parameters
        ----------
        user_id : uuid.UUID
        current_user_id : str

        Raises
        ------
        ResourceNotFound
            If the user_id does not correspond to an existing user.
        ForbiddenError
            If a user attempts to delete their own account.
        '''
        if not (existing := await self.users.get_user(user_id)):
            raise ResourceNotFound('user')

        if str(existing.id) == current_user_id:
            raise ForbiddenError('self_delete_not_allowed')

        await self.users.delete(existing)

    async def list_users(self, query: UserQuery, page: PageParams) -> UserPage:
        '''
        Lists users based on the provided query parameters and pagination.

        Parameters
        ----------
        query : UserQuery
        page : PageParams

        Returns
        -------
        UserPage
        '''
        sql_query, total = await self.users.filter_by(
            with_role=query.with_role,
            search=query.search,
            logged_in_after=query.logged_in_after,
        )

        sql_query = sql_query.limit(page.limit).offset(page.offset)

        results = [
            UserSchema.convert(user)
            for user in await self.users.list_orms(sql_query)
        ]

        page_details = UserPage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )

        return UserPage(
            data=results,
            page=page_details
        )

    async def read_user(self, user_id: uuid.UUID) -> UserSchema:
        if not (existing := await self.users.get_user(user_id)):
            raise ResourceNotFound('user')
        return UserSchema.convert(existing)

    async def check_credentials(
        self,
        username: str,
        password: str
    ) -> InternalUser:
        '''
        Verifies the provided username and password against stored credentials.

        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        InternalUser

        Raises
        ------
        UnauthorizedAccess
            If the credentials are invalid.
        '''
        user_row = await self.users.get_internal_user(
            username=username
        )
        if not user_row:
            raise UnauthorizedAccess('invalid_credentials')

        user = InternalUser.convert(user_row)
        if not self.crypto_service.verify_password(
            plain=password,
            hashed=user.password_hash
        ):
            raise UnauthorizedAccess('invalid_credentials')


        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        await self.users.touch_last_login(user_id)

    async def increment_cver(self, user_id: uuid.UUID) -> None:
        await self.users.bump_credential_version(user_id)

    async def read_internal_user(self, user_id: uuid.UUID) -> InternalUser:
        if not (existing := await self.users.get_internal_user(user_id=user_id)):
            raise ResourceNotFound('user')
        return InternalUser.convert(existing)