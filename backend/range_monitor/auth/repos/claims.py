
from datetime import datetime

import msgspec
from redis.asyncio.client import Redis

from range_monitor.auth.services.claims import JwtClaim
from range_monitor.db.repos.redis import RedisRepo
from range_monitor.utils.msgspec_codec import MsgspecStructCodec


class ClaimsCache(msgspec.Struct):
    iat: int
    exp: int
    jti: str
    cver: int
    sub: str

    @property
    def time_to_live(self) -> int:
        return max(0, self.exp - int(datetime.now().timestamp()))


class RotationError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ClaimsBackend(RedisRepo):
    namespace = 'jwt_claims'

    def __init__(self, client: Redis) -> None:
        super().__init__(client, prefix=self.namespace)
        self._codec: MsgspecStructCodec[ClaimsCache] = MsgspecStructCodec(
            ClaimsCache)

    def refresh_key(self, jti: str) -> str:
        return self.key('refresh', jti)

    def blacklist_key(self, jti: str) -> str:
        return self.key('blacklist', jti)

    def cver_key(self, user_id: str) -> str:
        return self.key('cver', user_id)


    async def save(self, claim: JwtClaim) -> ClaimsCache:
        '''
        Save the given JWT claim to the cache.

        Parameters
        ----------
        claim : JwtClaim
            The JWT claim to save.
        '''
        payload = ClaimsCache(
            iat=claim.iat,
            exp=claim.exp,
            jti=claim.jti,
            cver=claim.cver,
            sub=claim.sub
        )

        await self.client.setex(
            name=self.refresh_key(claim.jti),
            value=msgspec.json.encode(payload),
            time=payload.time_to_live
        )
        return payload

    async def incr_cver(self, user_id: str) -> int:
        '''
        Increment the claim version for the given user ID.

        Parameters
        ----------
        user_id : str
            The user ID to increment the claim version for.

        Returns
        -------
        int
            The new claim version.
        '''
        return await self.client.incr(self.cver_key(user_id))

    async def fetch(self, refresh_jti: str) -> ClaimsCache | None:
        '''
        Fetch the JWT claim from the cache by its refresh JTI.

        Parameters
        ----------
        refresh_jti : str
            The refresh JTI of the JWT claim to fetch.

        Returns
        -------
        ClaimsCache | None
            The JWT claim if found, None otherwise.
        '''
        data = await self.client.get(self.refresh_key(refresh_jti))
        if data is None:
            return None
        return self._codec.decode(data)

    async def get_claims_error(self, user_claim: JwtClaim,) -> str | None:
        if await self.has_blacklisted(user_claim.jti):
            return 'token_blacklisted'

        if await self.is_claim_stale(user_claim.sub, user_claim.cver):
            return 'stale_claim'

        return None

    async def rotate_claim(
        self,
        *,
        old_jti: str,
        old_access_jti: str,
        new_claim: JwtClaim
    ) -> ClaimsCache:

        # note: getdel, prevents the "double rotate" race condition
        encoded_claim = await self.client.getdel(self.refresh_key(old_jti))
        if not encoded_claim:
            raise RotationError('refresh_expired')

        if not (old_claim := self._codec.decode(encoded_claim)):
            raise RotationError('invalid_claim')

        rotated = ClaimsCache(
            iat=new_claim.iat,
            exp=new_claim.exp,
            jti=new_claim.jti,
            cver=new_claim.cver,
            sub=new_claim.sub
        )

        pipe = self.client.pipeline()
        # always blacklist first, pipelines fail atomically
        pipe.setex(
            name=self.blacklist_key(old_jti),
            value='1',
            time=old_claim.time_to_live
        )
        pipe.setex(
            name=self.blacklist_key(old_access_jti),
            value='1',
            time=old_claim.time_to_live
        )
        pipe.setex(
            name=self.refresh_key(new_claim.jti),
            value=msgspec.json.encode(rotated),
            time=rotated.time_to_live
        )

        await pipe.execute()
        return rotated

    async def has_blacklisted(self, jti: str) -> bool:
        '''
        Check if the given JTI is blacklisted.

        Parameters
        ----------
        jti : str
            The JTI to check.

        Returns
        -------
        bool
            True if the JTI is blacklisted, False otherwise.
        '''
        exists = await self.client.exists(self.blacklist_key(jti))
        return bool(exists)

    async def ensure_cver(self, user_id: str, user_cver: int) -> None:
        '''
        Ensure that the credential version for the given user ID is the one
        in the database upon login.

        Parameters
        ----------
        user_id : str
            The user ID to ensure the claim version for.
        user_cver : int
            The claim version to ensure.

        Returns
        -------
        int
            The current claim version.
        '''
        key = self.cver_key(user_id)

        await self.client.set(key, user_cver)

    async def is_claim_stale(self, user_id: str, token_cver: int) -> bool:
        '''
        Check if the given claim version is stale for the given user ID.

        Parameters
        ----------
        user_id : str
            The user ID to check.
        token_cver : int
            The claim version to check.

        Returns
        -------
        bool
            True if the claim version is stale, False otherwise.
        '''
        key = self.cver_key(user_id)
        current = await self.client.get(key)
        if current is None:
            return False

        current_cver = int(current)
        return current_cver > token_cver

    async def revoke_claim(self, claim: JwtClaim, access_jti: str) -> None:
        '''
        Revoke the given JWT claim.

        Parameters
        ----------
        claim : JwtClaim
            The JWT claim to revoke.

        Returns
        -------
        None
        '''
        pipe = self.client.pipeline()
        pipe.setex(
            name=self.blacklist_key(claim.jti),
            value='1',
            time=claim.time_to_live
        )
        pipe.setex(
            name=self.blacklist_key(access_jti),
            value='1',
            time=claim.time_to_live
        )
        await pipe.execute()

    async def get_cver(self, user_id: str) -> int | None:
        '''
        Get the claim version for the given user ID.

        Parameters
        ----------
        user_id : str
            The user ID to get the claim version for.

        Returns
        -------
        int
            The claim version.
        '''
        key = self.cver_key(user_id)
        current = await self.client.get(key)
        return int(current) if current else None

    async def blacklist_jti(self, jti: str, ttl: int) -> None:
        '''
        Blacklist the given JTI for the given time-to-live.

        Parameters
        ----------
        jti : str
            The JTI to blacklist.
        ttl : int
            The time-to-live in seconds.

        Returns
        -------
        None
        '''
        await self.client.setex(
            name=self.blacklist_key(jti),
            value='1',
            time=ttl
        )