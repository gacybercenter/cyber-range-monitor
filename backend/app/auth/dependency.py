from typing import Annotated
from fastapi import Depends, Request, Response

from app.core.errors import HTTPInvalidAPIKey

from app.extensions.redis.dependency import RedisClient, redis_client_maker

from .const import AUTH_COOKIE_NAME, API_KEY_AUTH_MODEL
from .schemas import ClientIdentity, APIKeyPayload
from .service import APIKeyProvider, APIKeyStore


RedisAuthDep = Annotated[RedisClient, Depends(
    redis_client_maker('auth:api_key:')
)]

async def get_key_provider(redis_conn: RedisAuthDep) -> APIKeyProvider:
    '''chains redis dependency to create a key provider dependency
    Arguments:
        redis_conn {RedisDep} -- the redis client 
    Returns:
        APIKeyProvider -- the api key provider instance
    '''
    key_store = APIKeyStore(redis_conn)
    return APIKeyProvider(
        cookie_name=AUTH_COOKIE_NAME,
        key_store=key_store
    )


async def get_client_identity(request: Request) -> ClientIdentity:
    '''dependency to get the client identity from the request'''
    return await ClientIdentity.create(request)


ClientIdentityDep = Annotated[ClientIdentity, Depends(get_client_identity)]
APIKeyCookieDep = Annotated[str, Depends(API_KEY_AUTH_MODEL)]
KeyProviderDep = Annotated[APIKeyProvider, Depends(get_key_provider)]


async def get_key_identity(
    signed_api_key: APIKeyCookieDep,
    key_provider: KeyProviderDep,
    client: ClientIdentityDep,
    response: Response
) -> APIKeyPayload:
    '''Gets the signed api key cookie and ensures that the cookie was 
    created under the same client, the client's key hasn't expired or 
    has been revoked and extends the key's lifetime if it hasn't expired
    for the client.

    Arguments:
        signed_api_key {APIKeyDep} -- the cookie on the client titled API_KEY_COOKIE_NAME
        key_provider {KeyProviderDep} -- the key provider dependency
        client {ClientIdentityDep} -- the identity of the client making the request
        response {Response} -- the response to revoke the key from the client if it's invalid
    Raises:
        HTTPInvalidAPIKey: if the key is invalid or missing from the client 
    Returns:
        APIKeyPayload -- the payload of the key
    '''
    if not signed_api_key:
        raise HTTPInvalidAPIKey()
    # reset the api key expiration in redis if valid and return the payload
    key_payload = await key_provider.get_key_data(signed_api_key, client)
    print('\n\n\n\nhere\n\n\n\n')
    if not key_payload:
        await key_provider.revoke_key(signed_api_key, response)
        raise HTTPInvalidAPIKey()
    return key_payload

AuthDep = Annotated[APIKeyPayload, Depends(get_key_identity)]
