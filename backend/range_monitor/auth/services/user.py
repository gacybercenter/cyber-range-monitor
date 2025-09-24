
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.auth.errors import InvalidCredentialsError
from range_monitor.auth.repos.claims import ClaimsBackend
from range_monitor.auth.repos.users import UserAuth, UserRepository
from range_monitor.auth.schema import (
    UserCreateBody,
    UserPage,
    UserPatchBody,
    UserPatchProfile,
    UserQuery,
    UserSchema,
)
from range_monitor.auth.services.passwords import PasswordService
from range_monitor.errors import (
    BadRequest,
    ConflictError,
    ForbiddenError,
    ResourceNotFound,
    UnprocessableEntity,
)
from range_monitor.params import PageParams, TimestampParams
from range_monitor.security import PasswordPolicy


class UserService:
    def __init__(
        self,
        *,
        db: AsyncSession,
        password_policy: PasswordPolicy
    ) -> None:
        self.users: UserRepository = UserRepository(db)
        self.passwords: PasswordService = PasswordService(password_policy)


    async def create_user(self, params: UserCreateBody) -> UserSchema:
        '''
        Creates a new user in the system if the username is unique.

        Parameters
        ----------
        params : UserCreateBody

        Returns
        -------
        UserSchema

        Raises
        ------
        ConflictError
            If the username is already taken.
        '''
        username_unique = await self.users.read.username_unique(params.username)
        if not username_unique:
            raise ConflictError('username_taken')

        password_hash = await self.passwords.hash_password(params.password)


        new_user = await self.users.write.create_user(
            username=params.username,
            password_hash=password_hash,
            role=params.role
        )

        return UserSchema.convert(new_user)


    async def read_user(self, user_id: str) -> UserSchema:
        '''
        Reads a user by their ID.

        Parameters
        ----------
        user_id : str

        Returns
        -------
        UserSchema

        Raises
        ------
        ResourceNotFound
            Provided user ID does not exist.
        '''
        user = await self.users.read.by_id(user_id)
        if not user:
            raise ResourceNotFound('user')
        return UserSchema.convert(user)

    async def patch_user(
        self,
        user_id: str,
        params: UserPatchBody | UserPatchProfile,
    ) -> UserSchema:
        '''
        Partial update of a user. If the role or password changes,
        the credential version is incremented and after transaction,
        the `cver` is synced in Redis.

        Parameters
        ----------
        user_id : str
        params : UserPatchBody
        claims : ClaimsBackend

        Returns
        -------
        UserSchema

        Raises
        ------
        ResourceNotFound
            Provided user ID does not exist.
        BadRequest
            No fields provided to update.
        ConflictError
            Username is already taken.
        UnprocessableEntity
            Failed to patch the user.
        '''
        if not (user := await self.users.read.by_id(user_id)):
            raise ResourceNotFound('user')


        if not (args := params.dump()):
            raise BadRequest('no_fields_provided')

        if plain_pwd := args.pop('password', None):
            args['password_hash'] = await self.passwords.hash_password(plain_pwd)

        if params.username and not await self.users.read.username_unique(
            params.username,
            excluding_id=user_id
        ):
            raise ConflictError('username_taken')


        patched_user = await self.users.write.patch_user(user, args)
        if not patched_user:
            raise UnprocessableEntity('cannot_patch_user')

        return UserSchema.convert(patched_user)

    async def delete_by_id(self, user_id: str, actor_id: str) -> None:
        '''
        Deletes a user by their ID.

        Parameters
        ----------
        user_id : str
        actor_id : str

        Raises
        ------
        ResourceNotFound
            Provided user ID does not exist.
        ForbiddenError
            Attempt to delete self.
        UnprocessableEntity
            Failed to delete the user.
        '''
        if not (user := await self.users.read.by_id(user_id)):
            raise ResourceNotFound('user')

        if user.id == actor_id:
            raise ForbiddenError('cannot_delete_self')

        success = await self.users.write.remove(user)

        if not success:
            raise UnprocessableEntity('cannot_delete_user')

        await self.users.write.transaction(commit=True)

    async def list_users_by(
        self,
        filters: UserQuery,
        page: PageParams,
        timestamps: TimestampParams
    ) -> UserPage:
        '''
        Lists users by the provided filters and paginates the results.

        Parameters
        ----------
        filters : UserQuery
        page : PageParams
        timestamps : TimestampParams | None

        Returns
        -------
        UserPage
        '''
        statement, count = await self.users.read.create_query(
            with_role=filters.with_role,
            search=filters.search,
            logged_in_after=filters.logged_in_after,
            timestamps=timestamps
        )

        if count == 0:
            return UserPage.from_results(
                data=[],
                page_number=page.page_number,
                page_size=page.page_size,
                total=0
            )

        dtos = []
        async for user in self.users.read.stream_scalars(
            statement,
            limit=page.limit,
            offset=page.offset
        ):
            dtos.append(
                UserSchema.convert(user)
            )

        return UserPage.from_results(
            data=dtos,
            page_number=page.page_number,
            page_size=page.page_size,
            total=count
        )

    async def authenticate(
        self,
        username: str,
        password: str
    ) -> UserAuth:
        '''
        Validates the given username and password combination.

        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        str
            The user ID if the credentials are valid.

        Raises
        ------
        UnauthorizedAccess
            If the credentials are invalid.
        '''
        user_auth = await self.users.read.get_user_auth(username)

        if not user_auth:
            raise InvalidCredentialsError()

        if not await self.passwords.verify_password(
            plaintext=password,
            stored_hash=user_auth.password_hash
        ):
            raise InvalidCredentialsError()

        await self.users.write.touch_last_login(user_auth.id)

        return user_auth
