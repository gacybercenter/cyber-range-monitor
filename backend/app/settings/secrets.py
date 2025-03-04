from pydantic import Field
from pydantic_settings import BaseSettings


class APISecrets(BaseSettings):
    """The "secrets" for the API, must be loaded from an ENV file,
    the env_file loaded is dependent on the "api_config.env_file" value
    and as such isn't defined here
    """

    secret_key: str = Field(..., description="The secret key for the API")
    signature_salt: str = Field(
        ..., description="The salt for the API signature when sessions are issued"
    )
    encryption_key: str = Field(..., description="The key for encrypting the session")
    csrf_key: str = Field(..., description="The key for CSRF protection")
    redis_password: str = Field(..., description="The password for the redis server")
