

from dataclasses import dataclass

from range_monitor.errors import (
    BadRequest,
    ForbiddenAccess,
    ResourceNotFound,
    UnprocessableEntity,
)
from range_monitor.security import SignatureProvider
from range_monitor.users.sessions import utils as session_utils
from range_monitor.users.sessions.backend import SessionBackend
from range_monitor.users.sessions.model import Session
from range_monitor.users.sessions.schema import (
    SessionClaim,
    UserSession,
    UserSessionList,
)


@dataclass(slots=True)
class SessionService:
    sessions: SessionBackend
    signatures: SignatureProvider

    def new_session(
        self,
        user_id: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        """
        Creates a new session for the given user ID.

        Parameters
        ----------
        user_id : UUID

        Returns
        -------
        Session
        """
        return Session(
            user_id=user_id,
            created_at=session_utils.utcnow(),
            session_id=Session.make_id(),
            last_seen=session_utils.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def create_session_claim(
        self,
        session: Session,
        *,
        save_claim: bool = True
    ) -> SessionClaim:
        """
        Stores a session and returns a LoginResponse.

        Parameters
        ----------
        session : Session
        signer : SignatureProvider

        Returns
        -------
        LoginResponse
        """
        idle_timeout_at = session_utils.idle_timeout_at(session.last_seen)
        max_age_at = session_utils.max_age_at(session.created_at)

        if save_claim:
            await self.sessions.save(
                session_id=session.session_id,
                session=session,
                idle_timeout=session_utils.idle_timeout_seconds(),
            )
        client_session_id = self.signatures.sign_message(session.session_id)

        return SessionClaim(
            session_id=client_session_id,
            created_at=session.created_at,
            idle_timeout_at=idle_timeout_at,
            max_age_at=max_age_at,
        )

    async def load_session(self, session_id: str) -> Session | None:
        """
        Retrieves and validates a session given a session ID.

        Parameters
        ----------
        session_id : str
            _The validated unsigned session ID_

        Returns
        -------
        Session | None
            _The session if valid or none if invalid_
        """
        if not (session := await self.sessions.read_session(session_id)):
            return None

        if session_utils.has_reached_idle_timeout(session.last_seen):
            await self.sessions.delete_session(session.session_id)
            return None

        if session_utils.has_reached_max_age(session.created_at):
            await self.sessions.delete_session(session.session_id)
            return None

        return session


    async def extend_session(self, session: Session) -> None:
        """
        Extends the session's last seen and updates it in the backend.

        Parameters
        ----------
        session : Session
            _The session to extend_
        """
        session.touch()
        await self.sessions.update_session(
            session=session,
            session_id=session.session_id,
            expires=session_utils.idle_timeout_seconds(),
        )


    async def revoke_session(self, session_id: str) -> None:
        """
        Removes a session given its ID.

        Parameters
        ----------
        session_id : str
        """
        await self.sessions.delete_session(session_id)


    async def list_user_sessions(self, user_id: str) -> UserSessionList:
        """
        Lists all sessions for a given user.

        Parameters
        ----------
        user_id : UUID
        sessions : SessionRepo

        Returns
        -------
        UserSessionList
        """
        session_list = await self.sessions.list_user_sessions(user_id)

        session_out = []
        for session in session_list:
            session_out.append(
                UserSession(
                    session_id=self.signatures.sign_message(session.session_id),
                    ip_address=session.ip_address,
                    user_agent=session.user_agent,
                    user_id=session.user_id,
                    created_at=session.created_at,
                )
            )

        return UserSessionList(sessions=session_out, total=len(session_out))


    async def revoke_all_sessions(self, user_id: str) -> None:
        return await self.sessions.delete_user_sessions(user_id=user_id)

    async def delete_session_by_id(
        self,
        *,
        current_user_id: str,
        current_session_id: str,
        session_id: str,
        is_admin: bool = False,
    ) -> None:
        """
        Revokes a session if it belongs to the current user,
        ensure your check the Role belongs to UserRoles.USER

        Parameters
        ----------
        current_user_id : str
            _The current authenticated user's ID_
        session_id : str
            _The session ID to revoke_

        Raises
        ------
        PermissionDenied
            _If the session does not belong to the current user_
        """
        raw_session_id = self.signatures.get_message(session_id)

        if not raw_session_id:
            raise UnprocessableEntity(
                'The provided session was tampered with or wasnt provided '
                'by this server.'
            )

        if raw_session_id == current_session_id:
            raise BadRequest(
                detail=(
                    'You cannot delete your current session via this endpoint, '
                    'use /auth/logout instead.'
                ),
                headers={
                    'Location': '/auth/logout'
                }
            )

        if not (session := await self.sessions.read_session(raw_session_id)):
            raise ResourceNotFound('Session not found')

        if session.user_id != current_user_id and not is_admin:
            raise ForbiddenAccess('Not authorized to delete this session')

        await self.sessions.delete_session(session_id=session_id)