from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from server.app import security
from server.app.errors.http import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from server.app.users.repo import (
    create_db_user,
    filter_users_by,
    get_internal_user,
    get_username_by_id,
    is_username_unique,
    touch_user_id,
    update_db_user,
)
from server.app.users.schema import (
    CreateUserBody,
    InternalUser,
    PatchUserBody,
    PatchUserProfile,
    UserPage,
    UserQuery,
    UserSchema,
)

if TYPE_CHECKING:
    from server.app.auth.repo import TokenStore
    from server.db.repos import SQLRepository
    from server.models import User
    from server.utils.paginate import PageParams


@dataclass(slots=True)
class UsersService:
    '''
    A service for managing Range Monitor users with CRUD,
    password hashing and methods to check credentials.
    '''

    users: SQLRepository[User]
    tokens: TokenStore

    async def get_user(self, user_id: uuid.UUID) -> UserSchema:
        '''
        Fetches user authentication details by ID.

        Parameters
        ----------
        user_id : uuid.UUID
            The ID of the user to fetch.

        Returns
        -------
        InternalUser | None
        '''
        if not (db_user := await self.users.read(user_id)):
            raise NotFoundError('user')

        return UserSchema.convert(db_user)

    async def create_user(
        self, body: CreateUserBody, creator_id: uuid.UUID
    ) -> UserSchema:
        '''
        Creates a new user in the system.

        Raises
        ------
        NotFoundError
            If the creator_id does not correspond to a
            valid user.
        ConflictError
            If the username is already taken.
        '''

        creator_name = await get_username_by_id(
            repo=self.users,
            user_id=creator_id,
        )

        if not creator_name:
            raise NotFoundError('creator_user')

        if not await is_username_unique(
            repo=self.users,
            username=body.username,
        ):
            raise ConflictError('username_taken')

        new_user = await create_db_user(
            users=self.users,
            password_hash=security.hash_password(body.password),
            creator_name=creator_name,
            username=body.username,
            role=body.role,
        )

        return UserSchema.convert(new_user)

    async def update_user(
        self,
        user_id: uuid.UUID,
        params: PatchUserBody | PatchUserProfile,
    ) -> UserSchema:
        """
        Updates an existing user's details.

        Raises
        ------
        NotFoundError
            If the user_id does not correspond to an existing user.
        ConflictError
            If the new username is already taken by another user.
        """

        if not (existing := await self.users.read(user_id)):
            raise NotFoundError('user')

        if params.username and not await is_username_unique(
            self.users, username=params.username, excluding_id=user_id
        ):
            raise ConflictError('username_taken')

        patch_args = params.model_dump(exclude_unset=True)

        if password := patch_args.pop('password', None):
            patch_args['password_hash'] = security.hash_password(password)

        await update_db_user(
            repo=self.users,
            user=existing,
            params=patch_args,
        )

        new_cver = existing.credential_version
        await self.tokens.set_cver(
            user_id=str(existing.id),
            cver=new_cver,
        )

        return UserSchema.convert(existing)

    async def delete_by_id(
        self,
        *,
        target_user: uuid.UUID,
        current_user: uuid.UUID,
    ) -> None:
        '''
        Deletes a user from the system.

        Parameters
        ----------
        target_user : uuid.UUID
            The ID of the user to delete.
        current_user : uuid.UUID
            The ID of the user performing the deletion.
        bg_tasks : BackgroundTasks
            The background tasks manager.

        Raises
        ------
        NotFoundError
            If the user_id does not correspond to an existing user.
        ForbiddenError
            If a user attempts to delete their own account.
        '''
        if not (target := await self.users.read(target_user)):
            raise NotFoundError('user')

        if target.id == current_user:
            raise ForbiddenError('cannot_delete_self')

        await self.users.delete(target)
        await self.tokens.incr_cver(str(target.id))
        await self.tokens.delete_user_tokens(str(target.id))

    async def list_users(self, query: UserQuery, page: PageParams) -> UserPage:
        '''
        Lists users based on the provided query parameters and pagination.

        Parameters
        ----------
        query : UserQuery
            Optional filters for querying users.
        page : PageParams
            Pagination parameters.

        Returns
        -------
        UserPage
        '''
        sql_query, total = await filter_users_by(self.users, query)

        sql_query = sql_query.limit(page.limit).offset(page.offset)

        results = [
            UserSchema.convert(row) async for row in self.users.stream_rows(sql_query)
        ]

        page_details = UserPage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )

        return UserPage(data=results, page=page_details)

    async def check_credentials(self, username: str, password: str) -> InternalUser:
        '''
        Verifies the provided username and password against stored credentials.

        Parameters
        ----------
        username : str
            The username to verify.
        password : str
            The password to verify.

        Returns
        -------
        InternalUser

        Raises
        ------
        UnauthorizedError
            If the credentials are invalid.
        '''

        user = await get_internal_user(repo=self.users, username=username)

        if not user:
            raise UnauthorizedError('invalid_credentials')

        if not security.verify_password(password, user.password_hash):
            raise UnauthorizedError('invalid_credentials')

        return user

    async def update_login_date(self, user_id: uuid.UUID) -> None:
        await touch_user_id(repo=self.users, user_id=user_id, mode='login')

    async def get_token_user(self, token_sub: str) -> InternalUser | None:
        user_id = uuid.UUID(token_sub)
        return await get_internal_user(repo=self.users, user_id=user_id)
