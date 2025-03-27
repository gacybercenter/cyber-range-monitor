import time
from typing import Optional

from .schemas import (
    APIKeyData, 
    ClientIdentity,
    KeyBearerIdentity,
    KeyInfo
)
from .api_key_store import APIKeyStore
from .const import KEY_MAX_LIFETIME, KEY_EXPIRATION


def max_age_reached(created_at: float) -> bool:
    """Checks if the session has reached the maximum lifetime"""
    key_lifetime = time.time() - created_at
    return key_lifetime > KEY_MAX_LIFETIME


class KeyBearerService:
    '''The APIKeyBearerService is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    '''

    def __init__(self, key_store: APIKeyStore) -> None:
        self._key_store: APIKeyStore = key_store

    async def assign_key(
        self,
        username: str,
        role: str,
        client_identity: ClientIdentity
    ) -> str:
        """Creates an API Key, encrypts the APIKeyData before storing it in redis and returns
        a signed api key id to be issued in the response.

        The server generates an API Key that is digitally signed and salted by the
        server corresponds to a an unsigned key to an encrypted redis dictionary based
        on "APIKeyData" which is set to expire after an hour.

        If the client sends another request to the API within the KEY_EXPIRATION (1 hour), the
        key is then extended to expire after another hour.

        Arguments:
            api_key {APIKeyData} -- The data to be stored in the session

        Returns:
            str -- The signed session id to be issued to the client
        """
        key_data = APIKeyData.create(
            username=username,
            role=role,
            client_identity=client_identity
        )
        signed_key = await self._key_store.create_and_store(
            key_data.model_dump(),
            KEY_EXPIRATION  # NOTE: it's important that this is NOT the max age
        )
        return signed_key

    async def get_key_data(
        self,
        signed_key: str,
        inbound_client: ClientIdentity
    ) -> APIKeyData | None:
        """gets the api key data from the signed_key from the client cookies and checks
        if the max lifetime is reached, if it was issued by the server and exists in the
        redis session store. The API key if the max lifetime hasn't been reached refreshes
        the session expiration in the redis store

        returns none if the session is invalid or expired

        Arguments:
            signed_id {str} -- the signed id in client cookies
            inbound_client {ClientIdentity} -- the inbound identity of the client

        Returns:
            Optional[APIKeyData]
        """

        key_payload = await self._key_store.get_key_data(
            signed_key, KEY_MAX_LIFETIME
        )
        print(f'\n\nkey_payload={key_payload}')
        if not key_payload:
            return None
        try:
            key_data = APIKeyData(**key_payload)
        except Exception:
            return None

        key_highjacked = not key_data.trusts_client(inbound_client)
        if max_age_reached(key_data.created_at) or key_highjacked:
            await self._key_store.delete_key(signed_key, KEY_MAX_LIFETIME)
            return None

        await self._key_store.extend_key_lifetime(
            signed_key,
            KEY_EXPIRATION,
            max_age=KEY_MAX_LIFETIME  # NOTE: this is the max age not the expiration
        )
        return key_data

    async def revoke(self, signed_key: Optional[str]) -> None:
        '''Delets the api key from both redis and the clients cookies
        Arguments:
            signed_key {Optional[str]} -- the signed api key
            response {Response} -- the response with the key deleted
        '''
        if signed_key:
            await self._key_store.delete_key(signed_key, KEY_MAX_LIFETIME)

    async def get_key_health(self, signed_key: str) -> KeyInfo:
        '''Gets the time to live of the api key in redis
        Arguments:
            signed_key {Optional[str]} -- the signed api key
        Returns:
            int -- the time to live in seconds
        '''
        invalid_key = KeyInfo(
            identity=None,
            next_exp=-1,
            max_ttl=0
        )

        next_exp = await self._key_store.get_key_ttl(signed_key, KEY_MAX_LIFETIME)

        key_data = await self._key_store.get_key_data(signed_key, KEY_MAX_LIFETIME)
        if not key_data:
            return invalid_key

        identity = key_data.get('identity')
        if not identity:
            return invalid_key

        try:
            key_identity = KeyBearerIdentity(
                **identity
            )
        except:
            return invalid_key

        return KeyInfo(
            identity=key_identity,
            next_exp=next_exp,
            max_ttl=KEY_MAX_LIFETIME
        )
