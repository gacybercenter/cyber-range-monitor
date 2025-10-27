from datetime import UTC, datetime
from typing import Literal, NamedTuple

from redis.asyncio import Redis


def blacklistkey(jti: str) -> str:
    return f'blacklist:token:{jti}'


def cverkey(user_id: str) -> str:
    return f'user:cver:{user_id}'


def csrfkey(csrf_token: str) -> str:
    return f'csrf:token:{csrf_token}'


def tokenkey(key: 'TokenKey') -> str:
    return f'token:{key.token_type}:{key.user_id}:{key.token_id}'


class TokenKey(NamedTuple):
    token_type: Literal['access', 'refresh']
    token_id: str
    user_id: str


class TokenStore:
    '''
    The TokenStore provides methods to manage session tokens
    '''

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def save_token(
        self,
        key: TokenKey,
        exp: int,
        metadata: dict[str, str] | None = None,
    ) -> bool:
        '''
        Saves a session token in Redis with associated metadata.
        '''
        pipe = self.redis.pipeline()
        redis_key = tokenkey(key)

        fields = {
            'user_id': key.user_id,
            'session_id': key.token_id,
            'token_type': key.token_type,
        }

        if metadata:
            non_null_meta = dict(filter(bool, metadata.items()))
            fields.update(non_null_meta)

        pipe.hset(redis_key, mapping=fields)  # type: ignore
        pipe.expire(redis_key, exp, nx=True)
        _, nx = await pipe.execute()
        return bool(nx)

    async def delete_token(self, key: TokenKey) -> None:
        await self.redis.delete(tokenkey(key))

    async def exists(self, key: TokenKey) -> bool:
        exists = await self.redis.exists(tokenkey(key))
        return bool(exists)

    async def delete_user_tokens(self, user_id: str) -> None:
        '''
        Revokes all tokens associated with a user.

        Parameters
        ----------
        user_id : str
            The user ID whose tokens are to be revoked.
        '''
        pattern = f'token:*:{user_id}:*'

        keys = [key async for key in self.redis.scan_iter(pattern)]
        if not keys:
            return

        pipeline = self.redis.pipeline()
        for key in keys:
            pipeline.delete(key)
        await pipeline.execute()

    async def list_session_data(self, user_id: str) -> list[dict[str, str]]:
        '''
        Retrieves all session tokens and their metadata for a given user.

        Parameters
        ----------
        user_id : str
            The user ID whose session tokens are to be listed.

        Returns
        -------
        list[dict[str, str]]
        '''
        pattern = f'token:refresh:{user_id}:*'
        session_keys = [key async for key in self.redis.scan_iter(pattern)]
        if not session_keys:
            return []

        pipe = self.redis.pipeline()
        for key in session_keys:
            pipe.hgetall(key)

        fetched = await pipe.execute()
        return [sess for sess in fetched if sess]

    async def delete_session_tokens(self, session_id: str, user_id: str) -> bool:
        token_types = ('access', 'refresh')
        keys = (
            TokenKey(token_type=tt, token_id=session_id, user_id=user_id)
            for tt in token_types
        )
        pipe = self.redis.pipeline()
        for key in keys:
            pipe.delete(tokenkey(key))

        result = await pipe.execute()
        return all(res > 0 for res in result)

    async def update_activity(self, user_id: str, session_id: str) -> None:
        redis_key = tokenkey(
            TokenKey(
                token_type='access',
                token_id=session_id,
                user_id=user_id,
            )
        )

        await self.redis.hset(  # type: ignore
            redis_key, key='last_active', value=datetime.now(UTC).isoformat()
        )

    async def set_cver(self, user_id: str, cver: int) -> None:
        '''
        Sets the credential version (cver) for a user.
        '''
        await self.redis.set(cverkey(user_id), cver)

    async def verify_cver(self, user_id: str, cver: int) -> bool:
        '''
        Ensures the provided credential version matches the stored version.
        '''
        stored_cver = await self.redis.get(cverkey(user_id))
        if stored_cver is None:
            return False
        return int(stored_cver) == cver

    async def incr_cver(self, user_id: str) -> int:
        '''
        Bumps the credential version for a user, invalidating existing tokens.
        '''
        return await self.redis.incr(cverkey(user_id))
