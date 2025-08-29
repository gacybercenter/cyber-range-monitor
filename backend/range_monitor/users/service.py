from __future__ import annotations

from typing import TYPE_CHECKING

from range_monitor.errors import (
    BadRequest,
    ResourceNotFound,
    UnprocessableEntity,
)
from range_monitor.security import PasswordHashes

from .model import User
from .repo import UserRepo
from .schema import (
    AdminUpdateUserBody,
    CreateUserBody,
    UserListResponse,
    UserQuery,
    UserSchema,
    UserUpdateSelfBody,
)

if TYPE_CHECKING:
    pass


UserWriteParams = CreateUserBody | AdminUpdateUserBody | UserUpdateSelfBody



class UserService:
    def __init__(self, users: UserRepo, passwords: PasswordHashes) -> None:
        self.users: UserRepo = users
        self.passwords: PasswordHashes = passwords

    async def read(self, user_id: str) -> User:
        if not (user := await self.users.get_entity(user_id)):
            raise ResourceNotFound('User not found.')
        return user

    async def get(self, user_id: str) -> UserSchema:
        user = await self.read(user_id)
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
            raise BadRequest(detail='Username is already taken.')

        user_args = self.prepare_user_password(params)

        new_user = await self.users.create(
            params=user_args,
            auto_commit=True
        )

        if not new_user:
            raise UnprocessableEntity('Could not create user with the provided data.')

        return new_user

    async def update_user_id(
        self,
        user_id: str,
        params: UserUpdateSelfBody | AdminUpdateUserBody
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

        selected_user = await self.read(user_id)
        args = self.prepare_user_password(params)
        if not args:
            raise BadRequest(detail='No valid fields to update.')

        updated_user = await self.users.update(selected_user, **args)
        return UserSchema.convert(updated_user)

    async def list_users(self, filters: UserQuery) -> UserListResponse:
        query = self.users.query(
            with_role=filters.role,
        )

        paged_query = filters.paginate(query)
        total_rows = await self.users.count_total_rows(query)

        output = []
        async for user in self.users.stream_query(paged_query, schema=UserSchema):
            output.append(user)

        return UserListResponse.from_results(
            data=output,
            total=total_rows,
            page_size=filters.page_size,
            page_number=filters.page_number,
        )

    async def delete_user_id(self, target_id: str, actor_id: str) -> None:
        if target_id == actor_id:
            raise BadRequest(detail='You cannot delete your own user account.')

        target_user = await self.read(target_id)
        await self.users.delete(target_user)