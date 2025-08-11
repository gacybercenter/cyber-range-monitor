# import functools
# import logging
# import os
# import secrets

# from cryptography.fernet import Fernet
# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class SecretSettings(BaseSettings):
#     """The "secrets" for the API, must be loaded from an ENV file,
#     the env_file loaded is dependent on the "api_config.env_file" value
#     and as such isn't defined here
#     """

#     secret_key: str = Field(..., description="The secret key for the API")

#     signature_salt: str = Field(
#         ..., description="The salt for the API signature when sessions are issued"
#     )

#     encryption_key: str = Field(..., description="The key for encrypting the session")

#     encryption_salt: str = Field(..., description="The salt for encrypting the session")

#     csrf_key: str = Field(..., description="The key for CSRF protection")

#     redis_password: str = Field(..., description="The password for the redis server")

#     model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")


# class TempSecrets(SecretSettings):
#     """Non-persistent secrets for the API, used for
#     pipelines and testing. Note: after the API runs,
#     the secrets are lost and decrypting any encrypted
#     data will be impossible since the key is lost.
#     """

#     secret_key: str = secrets.token_urlsafe(32)
#     signature_salt: str = secrets.token_urlsafe(32)

#     encryption_key: str = Fernet.generate_key().decode()
#     encryption_salt: str = secrets.token_urlsafe(32)
#     csrf_key: str = secrets.token_urlsafe(32)

#     redis_password: str = "password"


# logger = logging.getLogger(__name__)


# @functools.lru_cache
# def get_secret_settings() -> SecretSettings:
#     """returns the secrets from the config.yml file
#     the LRU cache allows for the value to be computed once and reused
#     in subsequent calls
#     Returns:
#         SecretSettings -- the secrets from the config.yml file
#     """
#     if app_settings.testing:
#         return TempSecrets()

#     if not os.path.exists(app_settings.env_file):
#         logger.warning(
#             f"Config file {app_settings.env_file} does not exist, "
#             "using temp secrets, you may need to recreate the databse."
#         )
#         return TempSecrets()

#     return SecretSettings(
#         _env_file=app_settings.env_file,  # type: ignore
#     )
