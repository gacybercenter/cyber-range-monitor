
import base64
import secrets
from typing import NamedTuple

import itsdangerous
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import EnvConfig
from range_monitor.core.crypto import Encryptor, PasswordHashes, SignatureProvider


class SecuritySettings(EnvConfig):

    model_config = SettingsConfigDict(env_file='.env')

    secret_key: str
    signature_salt: str

    encryption_key: str
    encryption_key: str

    password_salt: str
    pbkdf2_iterations: int = 100_000
    pbkdf2_key_length: int = 32


class SecurityConnector:

    @staticmethod
    def encryptor(
        *,
        key: str,
        salt: str,
        iterations: int,
        length: int
    ) -> Encryptor:
        encoded_salt = salt.encode('utf-8')
        key_bytes = key.encode('utf-8')
        pdkdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=encoded_salt,
            iterations=iterations,
        )
        derived_key = pdkdf.derive(key_bytes)

        fernet = Fernet(base64.urlsafe_b64encode(derived_key))
        return Encryptor(fernet=fernet)

    @staticmethod
    def password_hasher(
        *,
        bcrypt_pepper: str
    ) -> PasswordHashes:
        context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return PasswordHashes(crypt_context=context, pepper=bcrypt_pepper)

    @staticmethod
    def signature_provider(
        *,
        secret_key: str,
        salt: str
    ) -> SignatureProvider:
        signer = itsdangerous.URLSafeTimedSerializer(
            secret_key,
            salt=salt,
        )
        return SignatureProvider(signer=signer)

    @staticmethod
    def temporary_settings() -> SecuritySettings:
        secret_key = secrets.token_urlsafe(32)
        sign_salt = secrets.token_urlsafe(16)
        encryption_key = Fernet.generate_key().decode()
        password_salt = secrets.token_urlsafe(16)
        return SecuritySettings(
            secret_key=secret_key,
            signature_salt=sign_salt,
            encryption_key=encryption_key,
            password_salt=password_salt,
        )

class SecurityBundle(NamedTuple):
    encryptor: Encryptor
    passwords: PasswordHashes
    signatures: SignatureProvider



def create_security_services(*, is_testing: bool = False) -> SecurityBundle:
    '''
    Initializes the security services from environment
    variables or temporary values for testing.

    Parameters
    ----------
    is_testing : bool, optional
        _If True, uses temporary random secrets_, by default False

    Returns
    -------
    ApplicationSecurity
    '''
    if is_testing:
        settings = SecurityConnector.temporary_settings()
    else:
        settings = SecuritySettings()  # type: ignore

    encryptor = SecurityConnector.encryptor(
        key=settings.encryption_key,
        salt=settings.password_salt,
        iterations=settings.pbkdf2_iterations,
        length=settings.pbkdf2_key_length,
    )

    passwords = SecurityConnector.password_hasher(
        bcrypt_pepper=settings.password_salt,
    )

    signature_service = SecurityConnector.signature_provider(
        secret_key=settings.secret_key,
        salt=settings.signature_salt,
    )

    return SecurityBundle(
        encryptor=encryptor,
        passwords=passwords,
        signatures=signature_service,
    )
