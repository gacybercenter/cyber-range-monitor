import secrets
import time
from typing import Optional

from fastapi import Response

from app.extensions.security import crypto

from app import config

from . import redis_key_store
from .schemas import APIKeyPayload, ClientIdentity, APIKeyPayload

key_config = config.get_api_key_config()


class APIKeyProvider:
    '''The API Key Provider is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for creating and deleting
    the cookies that contain the signed API Key that is used to retrieve the API Key from the
    redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    '''

    def __init__(self, cookie_name: str) -> None:
        self.cookie_name: str = cookie_name

    def create_signed_key(self) -> tuple:
        """Generates a session id that is used to store a session in redis"""
        raw_key = secrets.token_urlsafe(32)
        return crypto.create_signature(raw_key), raw_key

    def cookie_params(self, signed_key: str) -> dict:
        '''Creates the cookie parameters to set in the response

        Arguments:
            signed_key {str} -- the signed key to set in the cookie

        Returns:
            dict -- the cookie parameters
        '''
        return {
            'key': self.cookie_name,
            'value': signed_key,
            **key_config.cookie_options()
        }

    def key_max_age_reached(self, api_key: APIKeyPayload) -> bool:
        """Checks if the session has reached the maximum lifetime"""
        key_lifetime = time.time() - api_key.created_at
        return key_lifetime > key_config.key_max_lifetime()

    def resolve_signature(self, signed_api_key: str) -> str | None:
        '''Resolves the signed api key to the unsigned api key
        that can be used in the redis store
        Arguments:
            signed_api_key {str} -- the signed api key
        Returns:
            str | None -- the unsigned api key or none if the signature is invalid
        '''
        try:
            return crypto.load_signature(
                signed_api_key, 
                max_age=key_config.key_max_lifetime()
            )
        except Exception:
            return None

    async def store_api_key(self, api_key: APIKeyPayload) -> str:
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
        unsigned_key = secrets.token_urlsafe(32)
        signed_key = crypto.create_signature(unsigned_key) 
        await redis_key_store.set_api_key(
            unsigned_key,
            api_key.model_dump(),
            ex=key_config.client_key_lifetime()
        )
        return signed_key

    async def create_key_cookie(
        self,
        username: str,
        role: str,
        client_identity: ClientIdentity
    ) -> dict:
        """Creates an APIKeyPayload from the authenticated user, stores it in the
        Redis Store and returns the kwargs to set a cookie in the response

        Returns:
            dict -- the kwargs to set a cookie in the response with the api key as the value
        """
        client_identity.set_mapped_user(username)
        key_payload = APIKeyPayload.create(
            username=username,
            role=role,
            client_identity=client_identity
        )
        signed_id = await self.store_api_key(key_payload)
        return self.cookie_params(signed_id)

    async def get_payload(self, signed_key: str, inbound_client: ClientIdentity) -> APIKeyPayload | None:
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

        unsigned_api_key = self.resolve_signature(signed_key)
        if not unsigned_api_key:
            return None

        api_key_dump = await redis_key_store.get_api_key(unsigned_api_key)
        if not api_key_dump:
            return None
        try:
            api_key = APIKeyPayload(**api_key_dump)
        except Exception:
            return None

        session_highjacked = not api_key.trusts_client(inbound_client)
        if self.key_max_age_reached(api_key) or session_highjacked:
            await redis_key_store.delete_api_key(unsigned_api_key)
            return None

        # refresh the session expiration / extend for another "client_key_lifetime"
        await redis_key_store.set_key_exp(
            unsigned_api_key,
            key_config.client_key_lifetime()
        )

        return api_key

    async def delete_key(self, signed_key: str) -> None:
        """Loads the signed session ID, removes it from the redis store

        Arguments:
            signed_id {str} -- the signed id in client cookies
        """
        unsigned_api_key = self.resolve_signature(signed_key)
        if not unsigned_api_key:
            return
        await redis_key_store.delete_api_key(unsigned_api_key)

    async def revoke_key(self, signed_key: Optional[str], response: Response) -> None:
        '''Delets the api key from both redis and the clients cookies
        Arguments:
            signed_key {Optional[str]} -- the signed api key
            response {Response} -- the response with the key deleted
        '''
        if signed_key:
            await self.delete_key(signed_key)
        response.delete_cookie(self.cookie_name)
