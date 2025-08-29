from dataclasses import dataclass, field

from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from range_monitor.depends import RedisDep
from range_monitor.users.sessions.model import Session
from range_monitor.utils.msgspec_codec import MsgspecStructCodec


@dataclass(slots=True)
class SessionBackend:
    """
    A backend for managing user sessions using Redis.

    Returns
    -------
    _type_
        _description_

    Yields
    ------
    _type_
        _description_
    """

    client: Redis
    namespace: str = field(default='session', init=False)
    codec: MsgspecStructCodec[Session] = field(
        default_factory=lambda: MsgspecStructCodec(Session),
        init=False
    )

    def key(self, *parts: str) -> str:
        return ':'.join((self.namespace, *parts))

    def k_session(self, session_id: str) -> str:
        return self.key('record', session_id)

    def k_user(self, user_id: str) -> str:
        return self.key('users', user_id)

    async def save(
        self,
        *,
        session_id: str,
        session: Session,
        idle_timeout: int
    ) -> None:
        """
        Stores a session record and backmaps it to the user id,
        both with the given idle timeout.

        Parameters
        ----------
        session_id : str
        session : Session
        idle_timeout : int
        """
        session_key = self.k_session(session_id)
        user_sessions_key = self.k_user(str(session.user_id))

        pipe: Pipeline = self.client.pipeline(transaction=True)

        pipe.setex(session_key, idle_timeout, self.codec.encode(session))
        pipe.sadd(user_sessions_key, session_id)
        pipe.expire(user_sessions_key, idle_timeout)

        await pipe.execute()

    async def read_session(self, session_id: str) -> Session | None:
        """
        Retrieves a session.

        Parameters
        ----------
        session_id : str

        Returns
        -------
        Session | None
            _The session or none if it doesnt exist_
        """
        session_key = self.k_session(session_id)
        if not (raw := await self.client.get(session_key)):
            return None
        return self.codec.decode(raw)

    async def update_session(
        self,
        session: Session,
        session_id: str,
        *,
        expires: int | None = None
    ) -> None:
        """
        Updates a session record.

        Parameters
        ----------
        session : Session
        sid : str
            _The session id_
        expires : int | None, optional
            _The seconds to extend the session for_, by default None
        """
        session_key = self.k_session(session_id)
        if not expires:
            await self.client.set(session_key, self.codec.encode(session), ex=expires)
            return
        pipeline = self.client.pipeline(transaction=True)
        pipeline.set(session_key, self.codec.encode(session), ex=expires)
        pipeline.expire(self.k_user(session.user_id), expires)
        await pipeline.execute()

    async def delete_session(self, session_id: str) -> bool:
        """
        Deletes a session record removing both the
        session record and the backmap to the user
        id.

        Parameters
        ----------
        session_key : str

        Returns
        -------
        bool
        """
        if not (session := await self.read_session(session_id)):
            return False

        user_sessions_key = self.k_user(str(session.user_id))
        pipe = self.client.pipeline(transaction=True)

        pipe.delete(self.k_session(session_id))
        pipe.srem(user_sessions_key, session_id)

        result = await pipe.execute()
        return result[0] > 0 if result else False

    async def list_session_ids(self, user_id: str) -> list[str]:
        """
        gets a list of all the redis keys backmapped to a user

        Parameters
        ----------
        user_id : str

        Returns
        -------
        list[str]
        """
        raw_ids = await self.client.smembers(self.k_user(user_id))  # type: ignore
        if not raw_ids:
            return []
        return [sid.decode() if isinstance(sid, bytes) else sid for sid in raw_ids]

    async def iter_sessions(self, user_id: str, *, none_okay: bool = False):
        """
        Iterates over all the sessions for a user
        yielding the unsigned session id and the
        encoded session or None if the session is stale.

        Parameters
        ----------
        user_id : str
        none_okay : bool, optional
            _whether none should be yield_, by default False

        Yields
        ------
        tuple[str, bytes | None]
            _(session id, encoded session or None)_
        """
        ids = await self.list_session_ids(user_id)

        sessions = await self.client.mget(
            [self.k_session(session_id) for session_id in ids]
        )

        for i, encoded_session in enumerate(sessions):
            if not encoded_session and not none_okay:
                continue
            yield ids[i], encoded_session

    async def delete_user_sessions(self, user_id: str) -> None:
        """
        Deletes all the session records for a user
        Parameters
        ----------
        user_id : str
        """
        user_session_ids = await self.list_session_ids(user_id)

        pipe = self.client.pipeline(transaction=True)
        for session_id in user_session_ids:
            session_key = self.k_session(session_id)
            pipe.delete(session_key)

        pipe.delete(self.k_user(user_id))
        await pipe.execute()

    async def list_user_sessions(self, user_id: str) -> list[Session]:
        """
        Lists all the valid sessions for a user

        Parameters
        ----------
        user_id : str

        Returns
        -------
        list[Session]
        """
        session_keys = await self.list_session_ids(user_id)
        if not session_keys:
            return []

        sessions: list[Session] = []
        async for _, encoded_session in self.iter_sessions(user_id):
            if session := self.codec.decode(encoded_session):
                sessions.append(session)
        return sessions


async def get_session_backend(redis: RedisDep) -> SessionBackend:
    return SessionBackend(redis)
