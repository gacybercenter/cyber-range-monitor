'''
Contains all of the security policies for the application
that are loaded once at application startup.
'''

import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import timedelta
from typing import Self

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

from range_monitor.config import AuthConfig
from range_monitor.security.config import CryptoConfig, JwtConfig


def generate_secret_key(length: int = 32) -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_fernet_key() -> str:
    return Fernet.generate_key().decode('utf-8')


class EncryptionPolicy:
    '''
    Policy for encrypting and decrypting messages using fernet
    '''

    def __init__(
        self,
        fernet_key: str,
        *,
        salt: str,
        pbkdf2_iterations: int = 100_000,
        pbkdf2_key_length: int = 32
    ) -> None:
        derived_key = self._get_derived_key(
            fernet_key,
            salt=salt,
            pbkdf2_iterations=pbkdf2_iterations,
            pbkdf2_key_length=pbkdf2_key_length
        )
        self._fernet = Fernet(base64.urlsafe_b64encode(derived_key))

    def _get_derived_key(
        self,
        fernet_key: str,
        *,
        salt: str,
        pbkdf2_iterations: int,
        pbkdf2_key_length: int
    ) -> bytes:
        encoded_salt = salt.encode('utf-8')
        key_bytes = fernet_key.encode('utf-8')
        pdkdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=pbkdf2_key_length,
            salt=encoded_salt,
            iterations=pbkdf2_iterations,
        )
        return pdkdf.derive(key_bytes)

    @property
    def fernet(self) -> Fernet:
        return self._fernet


class PasswordPolicy:
    '''
    Policy for hashing and verifying passwords
    '''

    def __init__(
        self,
        *,
        bcrypt_pepper: str,
        bcrypt_rounds: int = 12
    ) -> None:
        self._bcrypt_ctx = CryptContext(
            schemes=['bcrypt'],
            bcrypt__rounds=bcrypt_rounds,
            deprecated='auto'
        )
        self._pepper: bytes = bcrypt_pepper.encode('utf-8')

    def compute_pepper(self, message: bytes) -> bytes:
        '''
        Applies a HMAC-SHA256 using the configured pepper

        Parameters
        ----------
        message : bytes

        Returns
        -------
        bytes
        '''
        return hmac.new(self._pepper, message, hashlib.sha256).digest()

    @property
    def bcrypt(self) -> CryptContext:
        return self._bcrypt_ctx


class JwtTokenPolicy:
    '''
    The configuration for the JWT tokens
    '''

    def __init__(
        self,
        jwt_secret: str,
        *,
        issuer: str,
        audience: str,
        key_id: str,
        token_ttl: dict[str, timedelta],
        algorithm: str = 'HS256',
        leeway: int = 0
    ) -> None:
        self._jwt_secret: str = jwt_secret
        self.issuer: str = issuer
        self.audience: str = audience
        self.algorithm: str = algorithm
        self._key_id: str = key_id
        self._token_ttl: dict[str, timedelta] = token_ttl
        self._leeway: int = leeway

    @property
    def jwt_headers(self) -> dict:
        '''
        The headers to include in the JWT token

        Returns
        -------
        dict
        '''
        return {
            'kid': self._key_id,
            'alg': self.algorithm,
            'typ': 'JWT',
        }

    @property
    def validation_options(self) -> dict:
        '''
        The options to use when decoding and validating a JWT token

        Returns
        -------
        dict
        '''
        return {
            'require_aud': True,
            'require_iss': True,
            'require_sub': True,
            'require_iat': True,
            'require_exp': True,
            'require_jti': True,
            'require_nbf': True,
            'leeway': self._leeway
        }

    @property
    def key(self) -> str:
        '''
        The secret key used to sign the JWT tokens

        Returns
        -------
        str
        '''
        return self._jwt_secret

    def get_token_ttl(self, token_type: str) -> timedelta:
        '''
        Gets the time-to-live duration for a given token type.

        Parameters
        ----------
        token_type : str

        Returns
        -------
        timedelta

        Raises
        ------
        RuntimeError
        '''
        if not (ttl := self._token_ttl.get(token_type)):
            raise RuntimeError(f'Unknown token type: {token_type}')
        return ttl

    def generate_jti(self) -> str:
        '''
        Generates a unique JWT ID (jti) for a token.

        Returns
        -------
        str
        '''
        return uuid.uuid4().hex


def create_jwt_token_policy(
    *,
    jwt_config: JwtConfig | None,
    auth_config: AuthConfig | None
) -> JwtTokenPolicy:
    jwt_config = jwt_config or JwtConfig()  # type: ignore
    auth_config = auth_config or AuthConfig()  # type: ignore

    return JwtTokenPolicy(
        jwt_secret=jwt_config.secret_key,
        issuer=auth_config.jwt_issuer,
        audience=auth_config.jwt_audience,
        key_id=jwt_config.kid,
        token_ttl={
            'access': auth_config.access_delta,
            'refresh': auth_config.refresh_delta
        },
        algorithm=jwt_config.algorithm,
        leeway=auth_config.token_leeway_seconds
    )


def create_encryption_policy(
    *,
    crypto_config: CryptoConfig | None
) -> EncryptionPolicy:
    crypto_config = crypto_config or CryptoConfig()  # type: ignore
    return EncryptionPolicy(
        fernet_key=crypto_config.fernet_key,
        salt=crypto_config.bcrypt_pepper,
        pbkdf2_iterations=crypto_config.pbkdf2_iterations,
        pbkdf2_key_length=crypto_config.pbkdf2_key_length
    )


def create_password_policy(
    *,
    crypto_config: CryptoConfig | None
) -> PasswordPolicy:
    crypto_config = crypto_config or CryptoConfig()  # type: ignore
    return PasswordPolicy(
        bcrypt_pepper=crypto_config.bcrypt_pepper,
        bcrypt_rounds=crypto_config.bcrypt_rounds if crypto_config else 12
    )


class SecurityPolicy:
    def __init__(
        self,
        *,
        jwt_config: JwtConfig | None = None,
        crypto_config: CryptoConfig | None = None,
        auth_config: AuthConfig | None = None
    ) -> None:
        jwt_config = jwt_config or JwtConfig()  # type: ignore
        crypto_config = crypto_config or CryptoConfig()  # type: ignore
        auth_config = auth_config or AuthConfig()  # type: ignore

        self.encryption: EncryptionPolicy = create_encryption_policy(
            crypto_config=crypto_config
        )
        self.passwords: PasswordPolicy = create_password_policy(
            crypto_config=crypto_config
        )
        self.jwt_token: JwtTokenPolicy = create_jwt_token_policy(
            jwt_config=jwt_config,
            auth_config=auth_config
        )

    @classmethod
    def testing_policy(cls) -> Self:
        '''
        Creates a temporary security policy with random secrets.
        Useful for testing or development.

        Returns
        -------
        SecurityPolicy
        '''
        temp_jwt_config = JwtConfig(
            secret_key=generate_secret_key(32),
            kid='temp-kid'
        )
        temp_crypto_config = CryptoConfig(
            fernet_key=generate_fernet_key(),
            bcrypt_pepper=generate_secret_key(16)
        )
        temp_auth_config = AuthConfig()

        return cls(
            jwt_config=temp_jwt_config,
            crypto_config=temp_crypto_config,
            auth_config=temp_auth_config
        )
