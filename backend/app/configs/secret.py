from pydantic import Field
from pydantic_settings import BaseSettings
from .config_init import settings_config

SECRETS_ENV_PREFIX = 'SECRET_'


class SecretsConfig(BaseSettings):
    '''The "secrets" for the API, must be 
    loaded from an ENV file 
    '''
    KEY: str = Field(
        ...,
        description='The secret key for the API'
    )
    SIGNATURE_SALT: str = Field(
        ...,
        description='The salt for the API signature when sessions are issued'
    )
    ENCRYPTION_KEY: str = Field(
        ...,
        description='The key for encrypting the session'
    )
    CSRF_KEY: str = Field(
        ...,
        description='The key for CSRF protection'
    )
    
    model_config = settings_config(SECRETS_ENV_PREFIX)