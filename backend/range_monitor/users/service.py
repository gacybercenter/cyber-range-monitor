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
    '''
    A service for managing Range Monitor users with CRUD,
    password hashing and methods to check credentials.
    '''
    def __init__(self, db: AsyncSession, crypto_service: CryptoService) -> None:
        self.users = UserRepository(db)
        self.crypto_service: CryptoService = crypto_service

    async def fetch(
        self,
        *,
        user_id: uuid.UUID | None = None,
        username: str | None = None
    ) -> InternalUser | None:
        '''
        Retrieves an internal user scheme not to be returned
        in API responses, but for use in the service layer.

        Parameters
        ----------
        user_id : uuid.UUID | None, optional
        username : str | None, optional

        Returns
        -------
        InternalUser
            _description_

        Raises
        ------
        ValueError
            No username or ID provided.
        '''
        if rows := await self.users.fetchuser(
            user_id=user_id,
            username=username
        ):
            return InternalUser.convert(rows)


        return None

    async def create_user(
        self,
        body: UserCreateBody,
        creator_id: uuid.UUID
    ) -> UserSchema:
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
        ResourceNotFound
            If the creator_id does not correspond to a
            valid user.
        ConflictError
            If the username is already taken.
        '''
        if not (creator := await self.fetch(user_id=creator_id)):
            raise ResourceNotFound('creator')

        if not await self.users.is_username_unique(body.username):
            raise ConflictError('username_taken')

        new_user = await self.users.create(
            username=body.username,
            password_hash=self.crypto_service.hash_password(body.password),
            role=body.role,
            created_by=creator.username
        )

        return UserSchema.convert(new_user)

    async def patch_by_id(
        self,
        user_id: uuid.UUID,
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

        if not (existing := await self.users.get(user_id)):
            raise ResourceNotFound('user')

        if params.username and not await self.users.is_username_unique(
            params.username,
            excluding_id=user_id
        ):
            raise ConflictError('username_taken')

        patch_args = params.model_dump(exclude_unset=True)

        if password := patch_args.pop('password', None):
            patch_args['password_hash'] = self.crypto_service.hash_password(password)

        await self.users.patch(existing, patch_args)
        return UserSchema.convert(existing)

    async def delete_by_id(
        self,
        user_id: uuid.UUID,
        current_user_id: uuid.UUID
    ) -> None:
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
        if not (target := await self.users.get(user_id)):
            raise ResourceNotFound('user')

        if target.id == current_user_id:
            raise ForbiddenError('cannot_delete_self')

        await self.users.delete(target)

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
        sql_query, total = await self.users.list_by(
            with_role=query.with_role,
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
        if not (existing := await self.users.get(user_id)):
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

        if not (user := await self.fetch(username=username)):
            raise UnauthorizedAccess('invalid_credentials')

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