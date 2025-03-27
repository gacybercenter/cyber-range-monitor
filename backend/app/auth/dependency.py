from typing import Annotated

from fastapi import Depends, Security, Request

from app.extensions.redis.dependency import RedisClient, redis_client_maker

from .api_key_store import APIKeyStore
from .schemas import ClientIdentity, APIKeyData
from .errors import (
    HTTPApiKeyRequired, HTTPInvalidApiKey
)
from .service import KeyBearerService
from .security import KeyBearerSecurity


async def get_client_identity(request: Request) -> ClientIdentity:
    '''dependency to get the client identity from the request'''
    return await ClientIdentity.create(request)

ClientIdentityDep = Annotated[ClientIdentity, Depends(get_client_identity)]

RedisAuthDep = Annotated[RedisClient, Depends(
    redis_client_maker('auth:api_key:')
)]


async def get_key_bearer_service(redis_conn: RedisAuthDep) -> KeyBearerService:
    '''chains redis dependency to create a key provider dependency
    Arguments:
        redis_conn {RedisDep} -- the redis client 
    Returns:
        KeyBearerService -- the api key provider instance
    '''
    key_store = APIKeyStore(redis_conn)
    return KeyBearerService(
        key_store=key_store
    )

KeyServiceDep = Annotated[KeyBearerService, Depends(get_key_bearer_service)]


async def get_key_bearer_identity(
    client: ClientIdentityDep,
    key: KeyBearerSecurity,
    key_service: KeyServiceDep
) -> APIKeyData:
    '''
    # API Authentication

    Gets the api key from the Authorization header and checks if the key is valid,
    exists in Redis, hasn't been highjacked and hasn't reached the max key age and 
    returns the key data if valid. If the key is invalid or missing, raises an
    HTTPInvalidApiKey exception. If the key is missing, raises an HTTPApiKeyRequired
    exception.

    Arguments:
        client {ClientIdentityDep} -- the identity of the client making the request
        api_key {OAuthKeySecurity} -- the security OAuth model
        key_service {KeyServiceDep} -- the key service dependency

    Raises:
        - HTTPApiKeyRequired: The api key is required but not provided
        - HTTPInvalidApiKey: The api key is invalid or has expired or has been revoked

    Returns:
        - APIKeyData -- the payload of the api key if valid
    '''

    if not key or not key.credentials:
        raise HTTPApiKeyRequired()
    api_key = key.credentials
    key_data = await key_service.get_key_data(api_key, client)
    if not key_data:
        raise HTTPInvalidApiKey()

    return key_data

AuthenticationDep = Annotated[APIKeyData, Security(get_key_bearer_identity)]
