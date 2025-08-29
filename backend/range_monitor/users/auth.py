from typing import TypedDict

from fastapi import Request

from range_monitor.core.request_parse import RequestAuditor
from range_monitor.errors import (
    UnauthorizedAccess,
)
from range_monitor.security import PasswordHashes
from range_monitor.users.repo import UserRepo
from range_monitor.users.schema import LoginResponse, UserSchema
from range_monitor.users.sessions.model import Session
from range_monitor.users.sessions.schema import UserSessionList
from range_monitor.users.sessions.service import SessionService


class Authorization(TypedDict):
    user: UserSchema
    session: Session


class AuthenticationService:
    def __init__(
        self,
        users: UserRepo,
        passwords: PasswordHashes,
        sessions: SessionService,
    ) -> None:
        self.users: UserRepo = users
        self.session_service: SessionService = sessions
        self.passwords: PasswordHashes = passwords

    async def check_credentials(self, username: str, password: str) -> UserSchema:
        """
        Validates user credentials and returns the user if valid.

        Parameters
        ----------
        username : str
        password : str
        pwd_hashes : PasswordHashes

        Returns
        -------
        User

        Raises
        ------
        UnauthorizedAccess
        UnauthorizedAccess
        """
        user = await self.users.get_by_username(username)
        if not user:
            raise UnauthorizedAccess('Invalid username or password.')

        if not self.passwords.check_password(
            plaintext=password,
            stored_hash=user.password_hash
        ):
            raise UnauthorizedAccess('Invalid username or password.')

        return UserSchema.convert(user)

    async def authenticate(self, request: Request, user: UserSchema) -> LoginResponse:
        """
        Logs in a user with the given credentials.

        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        LoginResponse
            _The login response containing the session ID and user info_

        Raises
        ------
        UnauthorizedAccess
            _Invalid username or password_
        """

        ip_address = RequestAuditor.get_request_ip(request)
        user_agent = request.headers.get('User-Agent')

        session = self.session_service.new_session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        claim = await self.session_service.create_session_claim(
            session,
            save_claim=True
        )

        return LoginResponse(
            username=user.username,
            role=user.role,
            user_id=user.id,
            session=claim,
        )

    async def get_authorization(self, unsigned_id: str) -> Authorization:
        """
        Gets the associated user for a session.

        Parameters
        ----------
        unsigned_id : str
            _The unsigned session ID from the client_


        Raises
        ------
        UnauthorizedAccess
            _The user no longer exists_
        ResourceNotFound
            _The session is invalid or expired_
        """
        session = await self.session_service.load_session(unsigned_id)
        if not session:
            raise UnauthorizedAccess('Invalid or expired session, please log in again.')

        user = await self.users.read_by_id(session.user_id)

        return Authorization(
            user=UserSchema.convert(user),
            session=session,
        )

    async def extend_authorization(self, auth: Authorization) -> None:
        """
        Extends the session's expiration.

        Parameters
        ----------
        auth : Authorization
            _The authorization containing the session to extend_
        """
        await self.session_service.extend_session(auth['session'])

    async def end_session(self, session_id: str) -> None:
        """
        Revokes a session by its ID.

        Parameters
        ----------
        session_id : str
            _The session ID to revoke_
        """
        await self.session_service.revoke_session(session_id)


    async def remove_all_sessions(self, user_id: str) -> None:
        """
        Revokes all sessions for a given user.

        Parameters
        ----------
        user_id : str
            _The user ID to revoke all sessions for_
        """
        await self.session_service.revoke_all_sessions(user_id)

    async def list_sessions(self, user_id: str) -> UserSessionList:
        """
        Lists all active sessions for a given user.

        Parameters
        ----------
        user_id : str
            _The user ID to list sessions for_

        Returns
        -------
        list[Session]
            _The list of active sessions for the user_
        """
        return await self.session_service.list_user_sessions(user_id=user_id)
