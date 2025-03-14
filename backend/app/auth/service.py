import time
from typing import Optional

from fastapi import Response

from app import config

from app.extensions.redis.dependency import RedisDep

from .schemas import APIKeyPayload, ClientIdentity, KeyStatus
from .api_key_store import APIKeyStore


auth_conf = config.get_config_yml().auth

class APIKeyProvider:
    '''The API Key Provider is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for creating and deleting
    the cookies that contain the signed API Key that is used to retrieve the API Key from the
    redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    '''

    def __init__(self, cookie_name: str, key_store: APIKeyStore) -> None:
        self.cookie_name: str = cookie_name
        self._key_store: APIKeyStore = key_store
        
    def auth_cookie(self, signed_key: str) -> dict:
        '''Creates the cookie parameters to set in the response

        Arguments:
            signed_key {str} -- the signed key to set in the cookie

        Returns:
            dict -- the cookie parameters
        '''
        return {
            'key': self.cookie_name,
            'value': signed_key,
            **auth_conf.cookie_options(),
        }

    def key_max_age_reached(self, api_key: APIKeyPayload) -> bool:
        """Checks if the session has reached the maximum lifetime"""
        key_lifetime = time.time() - api_key.created_at
        return key_lifetime > auth_conf.key_max_age()
    
    async def issue_key(
        self,        
        username: str,
        role: str,
        client_identity: ClientIdentity
    ) -> str:
        """Creates an API Key, encrypts an APIKeyPayload before storing it in redis and returns
        a signed api key id to be issued to the client.

        The server generates a session id that is digitally signed and salted by the
        server corresponds to a an unsigned key to an encrypted redis dictionary based
        on "APIKeyPayload".

        If the session id isn't used within the SESSION_EXPIRATION_SEC the session is removed from redis
        and the cookie containing the signed cookie will expire.

        Arguments:
            api_key {APIKeyPayload} -- The data to be stored in the session

        Returns:
            str -- The signed session id to be issued to the client
        """
        client_identity.set_mapped_user(username)
        key_payload = APIKeyPayload.create(
            username=username,
            role=role,
            client_identity=client_identity
        )
        signed_key = await self._key_store.create_key(
            key_payload.model_dump(),
            auth_conf.cookie_exp()
        )
        return signed_key
        
        
    async def get_key_data(
        self, 
        signed_key: str, 
        inbound_client: ClientIdentity
    ) -> APIKeyPayload | None:
        """gets the api key data from the signed_key from the client cookies and checks
        if the max lifetime is reached, if it was issued by the server and exists in the
        redis session store. The API key if the max lifetime hasn't been reached refreshes
        the session expiration in the redis store

        returns none if the session is invalid or expired

        Arguments:
            signed_id {str} -- the signed id in client cookies
            inbound_client {ClientIdentity} -- the inbound identity of the client

        Returns:
            Optional[APIKeyPayload]
        """

        key_payload = await self._key_store.get_key_payload(signed_key)
        if not key_payload:
            return None
        try:
            key_data = APIKeyPayload(**key_payload)
        except Exception:
            return None

        session_highjacked = not key_data.trusts_client(inbound_client)
        if self.key_max_age_reached(key_data) or session_highjacked:
            await self._key_store.remove_key(signed_key)
            return None
        
        await self._key_store.refresh_key_exp(
            signed_key,
            auth_conf.cookie_exp()
        )
        return key_data

    async def revoke_key(self, signed_key: Optional[str], response: Response) -> None:
        '''Delets the api key from both redis and the clients cookies
        Arguments:
            signed_key {Optional[str]} -- the signed api key
            response {Response} -- the response with the key deleted
        '''
        if signed_key:
            await self._key_store.remove_key(signed_key)
        response.delete_cookie(self.cookie_name)

    
    async def get_key_health(self, key_data: APIKeyPayload) -> KeyStatus:
        '''checks if the api key is still valid and other relevant information
        Arguments:
            key_data {APIKeyPayload} -- the api key data to check
        Returns:
            KeyStatus -- the status of the api key
        '''
        max_ttl = key_data.created_at + auth_conf.key_max_age()
        current_time = time.time()
        elapsed_time = current_time - key_data.created_at
        remaining_time = max_ttl - elapsed_time
        next_key_exp = key_data.created_at + auth_conf.key_max_age()
        return KeyStatus(
            key_exp=int(next_key_exp),
            assigned_to=key_data.username,
            max_ttl=int(remaining_time)
        )
        

    