

import base64
import hashlib
import hmac
import secrets
from datetime import timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext


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
    def crypt_context(self) -> CryptContext:
        return self._bcrypt_ctx

class JwtTokenPolicy:
    '''
    Policy for creating and validating JWT tokens
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
        '''
        The configuration for the JWT tokens

        Parameters
        ----------
        jwt_secret : str
            _The secret key used to sign the tokens._
        issuer : str
            _The issuer claim to include in the tokens._
        audience : str
            _The audience claim to include in the tokens._
        key_id : str
            _The KID to include in the token headers._
        token_ttl : dict[str, timedelta]
            _A mapping of token types to their time-to-live durations._
            example: {'access': timedelta(minutes=15), 'refresh': timedelta(days=7)}
        algorithm : str, optional
            _The alogrithm to use_, by default 'HS256'
        leeway : int, optional
            _The leeway (in seconds) to allow when validating token expiration_,
            by default 0
        '''
        self._jwt_secret: str = jwt_secret
        self.issuer: str = issuer
        self.audience: str = audience
        self._key_id: str = key_id
        self._token_ttl: dict[str, timedelta] = token_ttl
        self._algorithm: str = algorithm
        self._leeway: int = leeway

    def get_token_headers(self) -> dict:
        '''
        The headers to include in the JWT token

        Returns
        -------
        dict
        '''
        return {
            'kid': self._key_id,
            'alg': self._algorithm,
            'typ': 'JWT',
        }

    @property
    def decoder_options(self) -> dict:
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
        Generates a unique JWT ID (JTI) for a token.

        Returns
        -------
        str
        '''
        return base64.urlsafe_b64encode(secrets.token_bytes(16)).decode('utf-8').rstrip('=')