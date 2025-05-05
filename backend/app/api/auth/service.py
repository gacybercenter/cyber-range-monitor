from datetime import datetime
import time
from typing import Optional


from .schema import (
    SessionData,
    SessionHealth,
    ClientFingerprint,
    SessionInfo
)
from .session_store import SessionKeyStore

from .const import SESSION_EXPIRATION, SESSION_MAX_LIFETIME


def has_expired(start_time: float, duration: float) -> bool:
    """Calculates the time remaining before the key expires"""
    elapsed = time.time() - start_time
    remaining = duration - elapsed
    return remaining <= 0


class SessionService:
    '''The SessionService is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    '''

    def __init__(self, session_store: SessionKeyStore) -> None:
        self._session_store: SessionKeyStore = session_store

    async def assign_session(
        self,
        username: str,
        role: str,
        client: ClientFingerprint
    ) -> str:
        """Creates a session key, encrypts the SessionData before storing it in redis and returns
        a signed session key.

        The server generates a key that is digitally signed and salted by the
        server corresponding to a an unsigned key to an encrypted redis dictionary based
        on "SessionData" which is set to expire after an hour.

        If the client sends another request to the API within the SESSION_EXPIRATION (1 hour), the
        key is then extended to expire after another hour.

        Arguments:
            api_key {SessionData} -- The data to be stored in the session

        Returns:
            str -- The signed session id to be issued to the client
        """
        session_payload = SessionData.create(
            username=username,
            role=role,
            client=client
        )
        signed_key = await self._session_store.create_and_store(
            payload=session_payload.model_dump(),
            ex=SESSION_EXPIRATION  # NOTE: it's important that this is NOT the max age
        )
        return signed_key

    async def load_session(
        self,
        signed_key: str,
        inbound_client: ClientFingerprint
    ) -> SessionData | None:
        """gets the session data from the signed_key from the client cookies and checks
        if the max lifetime is reached, if it was issued by the server and exists in the
        redis session store. The API key if the max lifetime hasn't been reached refreshes
        the session expiration in the redis store

        returns none if the session is invalid or expired

        Arguments:
            signed_id {str} -- the signed id in client cookies
            inbound_client {ClientFingerprint} -- the inbound identity of the client

        Returns:
            Optional[SessionData]
        """

        session_payload = await self._session_store.get_session(
            signed_key=signed_key,
            max_age=SESSION_MAX_LIFETIME
        )
        if not session_payload:
            return None
        try:
            session_payload = SessionData(**session_payload)
        except Exception:
            return None

        session_highjacked = not session_payload.trusts_client(inbound_client)
        session_expired = has_expired(session_payload.created_at, SESSION_MAX_LIFETIME)
        if session_expired or session_highjacked:
            await self._session_store.delete_session(
                signed_key,
                SESSION_MAX_LIFETIME
            )
            return None

        await self._session_store.extend_session(
            signed_key=signed_key,
            ex=SESSION_EXPIRATION,
            max_age=SESSION_MAX_LIFETIME  # NOTE: this is the max age not the expiration
        )

        return session_payload

    async def revoke(self, signed_key: Optional[str]) -> None:
        '''Delets the api key from both redis and the clients cookies
        Arguments:
            signed_key {Optional[str]} -- the signed api key
            response {Response} -- the response with the key deleted
        '''
        if signed_key:
            await self._session_store.delete_session(signed_key, SESSION_MAX_LIFETIME)

    async def get_session_health(self, signed_key: str) -> SessionInfo | None:
        '''Gets the time to live of the api key in redis
        Arguments:
            signed_key {Optional[str]} -- the signed api key
        Returns:
            int -- the time to live in seconds
        '''
        session_dump = await self._session_store.get_session(signed_key, SESSION_MAX_LIFETIME)
        if not session_dump:
            return None
        try:
            session_payload = SessionData(**session_dump)
        except Exception:
            return None

        health = await self.inspect_session_health(session_payload, signed_key)
        return SessionInfo(
            owner=session_payload.identity,
            health=health
        )

    async def inspect_session_health(self, session_payload: SessionData, signed_key: str) -> SessionHealth:
        next_exp_ms = await self._session_store.get_session_ttl(
            signed_session_id=signed_key,
            max_age=SESSION_MAX_LIFETIME
        )
        next_exp = time.time() + next_exp_ms
        max_age_exp_seconds = session_payload.created_at + SESSION_MAX_LIFETIME
        return SessionHealth(
            max_age_at=datetime.fromtimestamp(max_age_exp_seconds),
            expires_next=datetime.fromtimestamp(next_exp),
            issued_at=datetime.fromtimestamp(session_payload.created_at)
        )
