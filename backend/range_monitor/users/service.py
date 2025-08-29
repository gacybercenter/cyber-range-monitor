from __future__ import annotations

from typing import TYPE_CHECKING

from range_monitor.errors import (
    BadRequest,
    UnprocessableEntity,
)
from range_monitor.params import TimestampParams
from range_monitor.security import PasswordHashes
from range_monitor.users.roles import UserRoles

from .model import User
from .repo import PageParams, UserRepo
from .schema import (
    CreateUserBody,
    UpdateProfileBody,
    UpdateUserBody,
    UserPageList,
    UserSchema,
)

if TYPE_CHECKING:
    pass


UserWriteParams = CreateUserBody | UpdateUserBody | UpdateProfileBody



class UserService:
    def __init__(self, users: UserRepo, passwords: PasswordHashes) -> None:
        self.users: UserRepo = users
        self.passwords: PasswordHashes = passwords


    async def read(self, user_id: str) -> UserSchema:
        '''
        Retrieve a user by their ID.

        Parameters
        ----------
        user_id : str
            _description_

        Returns
        -------
        UserSchema
        Raises
        ------
        ResourceNotFound
        '''
        user = await self.users.read_by_id(user_id)
        return UserSchema.convert(user)

    def prepare_user_password(self, params: UserWriteParams) -> dict:
        """
        Prepare user parameters for creating or updating a user,
        including hashing the password if provided.

        Parameters
        ----------
        params : UserWriteParams
        passwords : PasswordHashes

        Returns
        -------
        dict
            _The arguments ready to put in the db_
        """
        args = params.dump()
        if password := args.pop('password', None):
            args['password_hash'] = self.passwords.hash_password(password)
        return args

    async def create_user(self, params: CreateUserBody) -> User:
        if not await self.users.is_username_unique(params.username):
            raise BadRequest('Username is already taken.')

        user_args = self.prepare_user_password(params)

        try:
            new_user = self.users.create(**user_args)
        except Exception as e:
            raise UnprocessableEntity(
                'Could not create user with the provided data.'
            ) from e

        if not new_user:
            raise UnprocessableEntity('Could not create user with the provided data.')

        await self.users.save()
        return new_user

    async def update_user_id(
        self,
        user_id: str,
        params: UpdateProfileBody | UpdateUserBody
    ) -> UserSchema:
        """
        Update an existing user with the provided parameters.

        Parameters
        ----------
        user_id : UUID
        params : UpdateUserSchema
        repo : UserRepo

        Returns
        -------
        UserSchema

        Raises
        ------
        HTTPBadRequest
            _Username is taken or no valid fields to update_
        HTTPNotFound
            _User not found or invalid role provided_
        """

        selected_user = await self.users.read_by_id(user_id)
        args = self.prepare_user_password(params)
        if not args:
            raise BadRequest('No valid fields to update.')

        updated_user = await self.users.update(selected_user, params=args)
        return UserSchema.convert(updated_user)

    async def paginate_users(
        self,
        page: PageParams,
        timestamps: TimestampParams,
        with_role: UserRoles | None = None,
    ) -> UserPageList:
        '''
        Paginates users with optional filtering by role and timestamps.
        '''
        prepared_query = await self.users.query(
            page=page,
            timestamp=timestamps,
            with_role=with_role,
        )
        users_out = []
        async for user in self.users.stream(prepared_query.query):
            users_out.append(UserSchema.convert(user))

        return UserPageList.from_results(
            data=users_out,
            page_number=page.page_number,
            page_size=page.page_size,
            total=prepared_query.total,
        )


    async def delete_user_id(self, target_id: str, actor_id: str) -> None:
        '''
        Deletes a user by their ID, ensuring that the actor

        Parameters
        ----------
        target_id : str
            _The user to delete_
        actor_id : str
            _The user performing the delete_

        Raises
        ------
        BadRequest
            _If the user tries to delete themselves_
        '''
        if target_id == actor_id:
            raise BadRequest('You cannot delete your own user account.')

        target_user = await self.users.read_by_id(target_id)
        await self.users.delete(target_user)