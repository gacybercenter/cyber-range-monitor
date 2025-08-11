import base64
from typing import ClassVar

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from core import secrets

from . import const


def create_fernet(
    pkdf2_iterations: int = const.PBKDF2_ITERATIONS,
    pkdf2_key_length: int = const.PBKDF2_KEY_LENGTH,
) -> Fernet:
    """initializes fernet with the encryption key and salt from
    the secrets

    Returns:
        Fernet -- _the fernet instance_
    """
    secrets = secrets.get_secret_settings()
    encoded_salt = secrets.encryption_salt.encode("utf-8")
    key_bytes = secrets.encryption_key.encode("utf-8")
    pdkdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=pkdf2_key_length,
        salt=encoded_salt,
        iterations=pkdf2_iterations,
    )
    key = base64.urlsafe_b64encode(pdkdf.derive(key_bytes))
    return Fernet(key)


def create_serializer() -> URLSafeTimedSerializer:
    """initializes the URLSafeTimedSerializer with the secret key and salt

    Returns:
        URLSafeTimedSerializer -- _the URLSafeTimedSerializer instance_
    """
    secrets = secrets.get_secret_settings()
    return URLSafeTimedSerializer(secrets.secret_key, salt=secrets.signature_salt)


def create_crypto_context() -> CryptContext:
    """initializes the CryptContext with the PBKDF2 algorithm and bcrypt

    Returns:
        CryptContext -- _the CryptoContext instance_
    """
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


class CryptoServices:
    _fernet: ClassVar[Fernet] = create_fernet()
    _serializer: ClassVar[URLSafeTimedSerializer] = create_serializer()
    _bcrypt_ctx: ClassVar[CryptContext] = create_crypto_context()

    @classmethod
    def encrypt(cls, input_string: str) -> str:
        """
        Encrypts a string using fernet

        Parameters
        ----------
        input_string : str

        Returns
        -------
        str
        """
        return cls._fernet.encrypt(input_string.encode()).decode()

    @classmethod
    def decrypt(cls, input_string: str) -> str:
        """
        Decrypts fernet encrypted string

        Parameters
        ----------
        input_string : str

        Returns
        -------
        str
        """
        return cls._fernet.decrypt(input_string.encode()).decode()

    @classmethod
    def hash(cls, input_string: str) -> str:
        return cls._bcrypt_ctx.hash(input_string)

    @classmethod
    def verify_hash(cls, *, plain_text: str, hashed_text: str) -> bool:
        return cls._bcrypt_ctx.verify(plain_text, hashed_text)

    @classmethod
    def sign(cls, value: str) -> str:
        signature_salt = secrets.get_secret_settings().signature_salt
        return cls._serializer.dumps(value, salt=signature_salt)

    @classmethod
    def unsign(cls, value: str, max_age: int) -> str:
        signature_salt = secrets.get_secret_settings().signature_salt
        return cls._serializer.loads(value, salt=signature_salt, max_age=max_age)
