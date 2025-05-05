import secrets
from typing import Annotated

from cryptography.fernet import Fernet

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretSettings(BaseSettings):
    """The "secrets" for the API, must be loaded from an ENV file,
    the env_file loaded is dependent on the "api_config.env_file" value
    and as such isn't defined here
    """

    secret_key: Annotated[str, Field(
        ...,
        description="The secret key for the API"
    )]
    
    signature_salt: Annotated[str, Field(
        ...,
        description="The salt for the API signature when sessions are issued"
    )]
    
    encryption_key: Annotated[str, Field(
        ...,
        description="The key for encrypting the session"
    )]
    
    encryption_salt: Annotated[str, Field(
        ...,
        description="The salt for encrypting the session"
    )]
    
    csrf_key: Annotated[str, Field(
        ...,
        description="The key for CSRF protection"
    )]
    
    redis_password: Annotated[str, Field(
        ...,
        description="The password for the redis server"
    )]

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )


class TempSecrets(SecretSettings):
    '''Non-persistent secrets for the API, used for 
    pipelines and testing. Note: after the API runs,
    the secrets are lost and decrypting any encrypted 
    data will be impossible since the key is lost.
    '''
    secret_key: str = secrets.token_urlsafe(32)
    signature_salt: str = secrets.token_urlsafe(32)

    encryption_key: str = Fernet.generate_key().decode()
    encryption_salt: str = secrets.token_urlsafe(32)
    csrf_key: str = secrets.token_urlsafe(32)

    redis_password: str = 'password'
