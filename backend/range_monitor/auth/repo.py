from range_monitor.infra.repos import RedisRepository, redis_key


def blacklist_key(jti: str) -> str:
    return redis_key('blacklist', 'tokens', jti)

def cver_key(user_id: str) -> str:
    return redis_key('users', user_id, 'cver')

def jti_key(jti: str) -> str:
    return redis_key('refresh', 'token', jti)

def cver_lock(user_id: str) -> str:
    return redis_key('locks', 'cver', user_id)


def jti_lock(jti: str) -> str:
    return redis_key('locks', 'jti', jti)

class SessionRepository(RedisRepository):


    def jti_key(self, jti: str) -> str:
        return redis_key('refresh', 'token', jti)

    async def blacklist(self, jti: str, exp: int) -> None:
        '''
        Blacklists a JWT ID until its expiry time.

        Parameters
        ----------
        jti : str
            JWT ID to blacklist.
        exp : int
            Expiry time as a UNIX timestamp.
        '''
        await self.redis.set(blacklist_key(jti), '1', ex=exp)

    async def set_cver(self, user_id: str, cver: int) -> None:
        '''
        Sets the credential version for a user in Redis.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID.
        cver : int
            Credential version to set.
        '''
        await self.redis.set(cver_key(user_id), str(cver))

    async def is_blacklisted(self, jti: str) -> bool:
        '''
        Checks if a JWT ID is blacklisted.

        Parameters
        ----------
        jti : str
            JWT ID to check.

        Returns
        -------
        bool
            True if blacklisted, False otherwise.
        '''
        is_blacklisted = await self.redis.get(blacklist_key(jti))
        return is_blacklisted is not None

    async def get_cver(self, user_id: str) -> int | None:
        '''
        Retrieves the credential version for a user from Redis.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID.

        Returns
        -------
        int | None
            Credential version if set, None otherwise.
        '''
        cver = await self.redis.get(cver_key(user_id))
        return int(cver) if cver is not None else None

    async def soft_revoke_all(self, user_id: str) -> None:
        '''
        Soft revokes all sessions for a user by updating the credential version in Redis.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID whose sessions are to be revoked.
        new_cver : int
            New credential version to set.
        '''
        await self.set_cver(user_id, -1)

    async def verify_cver(self, user_id: str, token_cver: int) -> bool:
        '''
        Checks if the credential version in Redis matches the token's credential version.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID to check.
        token_cver : int
            Credential version from the token.

        Returns
        -------
        bool
            True if the versions match, False otherwise.
        '''
        redis_cver = await self.redis.get(cver_key(user_id))
        return (
            redis_cver is not None and
            int(redis_cver) == token_cver
        )

    async def save_claim(
        self,
        *,
        jti: str,
        user_id: str,
        cver: int,
        ttl: int
    ) -> bool:
        '''
        Saves a JWT claim in Redis, associating the JWT ID with the user ID and
        credential version.

        Parameters
        ----------
        jti : str
        user_id : str
        cver : int
        ttl : int

        Returns
        -------
        bool
        '''
        pipe = self.redis.pipeline()
        pipe.set(
            jti_key(jti),
            '1',
            ex=ttl,
            nx=True
        )
        pipe.set(cver_key(user_id), str(cver))
        set_result, _ = await pipe.execute()
        return set_result is True


    async def rotate(self, old_jti: str, new_jti: str, remaining_ttl: int) -> bool:
        '''
        Rotates the JWT ID for a session, blacklisting the old one and setting the new
        one.

        Parameters
        ----------
        old_jti : str
            Current JWT ID to be replaced.
        new_jti : str
            New JWT ID to set.
        remaining_ttl : int
            Remaining time to live for the new JWT ID in seconds.
        Returns
        -------
        bool
            True if rotation was successful, False if the old JWT ID was already
            blacklisted.
        '''
        if not await self.redis.set(
            jti_lock(old_jti),
            '1',
            ex=10,
            nx=True
        ):
            return False

        pipe = self.redis.pipeline()

        pipe.delete(jti_key(old_jti))
        pipe.set(
            blacklist_key(old_jti),
            '1',
            ex=remaining_ttl
        )
        pipe.set(
            self.jti_key(new_jti),
            '1',
            ex=remaining_ttl,
            nx=True
        )

        _, _, set_result = await pipe.execute()
        return set_result is True

    async def incr_cver(self, user_id: str) -> int:
        '''
        Increments the credential version for a user in Redis.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID whose credential version is to be incremented.

        Returns
        -------
        int
            The new credential version after incrementing.
        '''
        return await self.redis.incr(cver_key(user_id))