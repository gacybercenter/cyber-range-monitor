import secrets

from cryptography.fernet import Fernet
from pydantic import Field

from app.core.settings import Settings, load_secret_settings


class CryptoSettings(Settings):
    ENCRYPTION_KEY: str = Field(
        ..., description="The key used for encryption and decryption of sensitive data."
    )

    ENCRYPTION_SALT: str = Field(
        ...,
        description="The salt used for encryption and decryption of sensitive data.",
    )

    PBKDF2_ITERATIONS: int = Field(
        100_000,
        description="The number of iterations for the PBKDF2 key derivation function.",
    )

    PBKDF2_KEY_LENGTH: int = Field(
        32, description="The length of the key derived from PBKDF2."
    )

    SECRET_KEY: str = Field(
        ...,
        description="The secret key used for signing tokens and other cryptographic operations.",
    )

    SIGNATURE_SALT: str = Field(
        ...,
        description="The salt used for signing tokens and other cryptographic operations.",
    )

    BCRYPT_PEPPER: str = Field(
        ...,
        description="The pepper used for bcrypt hashing of passwords.",
    )


class TemporaryCryptoSecrets(CryptoSettings):
    """Temporary secrets for cryptographic operations."""

    ENCRYPTION_KEY: str = Fernet.generate_key().decode("utf-8")

    ENCRYPTION_SALT: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SIGNATURE_SALT: str = secrets.token_urlsafe(32)
    BCRYPT_PEPPER: str = secrets.token_urlsafe(32)


_crypto_settings: CryptoSettings = load_secret_settings(
    settings_class=CryptoSettings,
    testing_fallback_cls=TemporaryCryptoSecrets,
)


def get_crypto_settings_sync() -> CryptoSettings:
    return _crypto_settings


async def get_crypto_settings() -> CryptoSettings:
    return _crypto_settings
