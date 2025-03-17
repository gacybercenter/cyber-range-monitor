import json
import secrets

from app.extensions.security import crypto

from app.extensions.redis.client import RedisClient
from app import config

auth_conf = config.get_config_yml().auth

def resolve_signature(signed_key: str) -> str | None:
    '''Resolves the signed api key to the unsigned api key
    that can be used in the redis store
    Arguments:
        signed_key {str} -- the signed api key
    Returns:
        str | None -- the unsigned api key or none if the signature is invalid
    '''
    try:
        return crypto.load_signature(
            signed_key,
            auth_conf.key_max_age()
        )
    except Exception:
        return None


class APIKeyStore:
    def __init__(self, redis_conn: RedisClient) -> None:
        self._client = redis_conn

    async def create_key(
        self,
        payload: dict,
        ex: int | None = None
    ) -> str:
        '''creates an api key to assign to the client,
        stores the payload in the redis store and returns
        the signed key to be issued to the client
        Arguments:
            payload {dict} -- the payload to be stored in the redis store
        Keyword Arguments:
            ex {int | None} -- the seconds before the key expires
        Returns:
            str -- the signed key to be issued to the client
        '''
        unsigned_key = secrets.token_urlsafe(32)
        payload_str = json.dumps(payload)
        enc_payload = crypto.encrypt_data(payload_str)
        await self._client.set(unsigned_key, enc_payload, ex=ex)
        signed_key = crypto.create_signature(unsigned_key)
        return signed_key

    async def get_key_payload(self, signed_key: str) -> dict | None:
        '''resolves the signed key to the payload stored in redis

        Arguments:
            signed_key {str} -- the client's signed APIKey

        Returns:
            dict | None -- the payload stored in redis or None if the key is invalid
        '''
        unsigned_key = resolve_signature(signed_key)
        if not unsigned_key:
            return None
        encrypted_payload = await self._client.get(unsigned_key)
        if not encrypted_payload:
            return None
        payload = None
        try:
            payload_str = crypto.decrypt_data(encrypted_payload)
            payload = json.loads(payload_str)
        except Exception:
            pass
        return payload

    async def remove_key(self, signed_key: str) -> None:
        '''removes the key from the redis store

        Arguments:
            signed_key {str} -- the client's signed APIKey
        '''
        unsigned_key = resolve_signature(signed_key)
        if not unsigned_key:
            return
        await self._client.delete(unsigned_key)

    async def refresh_key_exp(self, signed_key: str, ex: int) -> None:
        '''refreshes the expiration time of the key in the redis store

        Arguments:
            signed_key {str} -- the client's signed APIKey
            ex {int} -- the new expiration time in seconds
        '''
        unsigned_key = resolve_signature(signed_key)
        if not unsigned_key:
            return
        await self._client.expire(unsigned_key, ex)
