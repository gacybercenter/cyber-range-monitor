from typing import ClassVar

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from itsdangerous import URLSafeTimedSerializer

from passlib.context import CryptContext

from app.core import settings

import base64
from .const import PBKDF2_ITERATIONS, PBKDF2_KEY_LENGTH


def initialize_ferent() -> Fernet:
    '''initializes fernet with the encryption key and salt from 
    the secrets

    Returns:
        Fernet -- _the fernet instance_
    '''
    secrets = settings.get_secret_settings()
    encoded_salt = secrets.encryption_salt.encode('utf-8')
    key_bytes = secrets.encryption_key.encode('utf-8')
    pdkdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=PBKDF2_KEY_LENGTH,
        salt=encoded_salt,
        iterations=PBKDF2_ITERATIONS
    )
    key = base64.urlsafe_b64encode(
        pdkdf.derive(key_bytes)
    )
    return Fernet(key)


def initialize_serializer() -> URLSafeTimedSerializer:
    '''initializes the URLSafeTimedSerializer with the secret key and salt

    Returns:
        URLSafeTimedSerializer -- _the URLSafeTimedSerializer instance_
    '''
    secrets = settings.get_secret_settings()
    return URLSafeTimedSerializer(
        secrets.secret_key,
        salt=secrets.signature_salt
    )


def initialize_hash_context() -> CryptContext:
    '''initializes the CryptContext with the PBKDF2 algorithm and bcrypt

    Returns:
        CryptContext -- _the CryptoContext instance_
    '''
    return CryptContext(
        schemes=["bcrypt"],
        deprecated="auto"
    )


class CryptoUtils:
    fernet: ClassVar[Fernet] = initialize_ferent()
    serializer: ClassVar[URLSafeTimedSerializer] = initialize_serializer()
    hash_context: ClassVar[CryptContext] = initialize_hash_context()

    @classmethod
    def encrypt(cls, input_string: str) -> str:
        """Encrypts a string using the fernet key

        Arguments:
            input_string {str} -- the string to encrypt
            length {int} -- the length of the key (default: {32})
        """
        return cls.fernet.encrypt(input_string.encode()).decode()

    @classmethod
    def decrypt(cls, input_string: str) -> str:
        """Decrypts a string using the fernet key

        Arguments:
            input_string {str} -- the string to decrypt
        """
        return cls.fernet.decrypt(input_string.encode()).decode()

    @classmethod
    def hash(cls, input_string: str) -> str:
        '''hashes a string using the PBKDF2 algorithm

        Arguments:
            input_string {str} -- _the string to hash_

        Returns:
            str -- _the hashed string_
        '''
        return cls.hash_context.hash(input_string)

    @classmethod
    def verify_hash(cls, plain_text: str, hashed_text: str) -> bool:
        ''' verifies a hash against a plain text string

        Arguments:
            plain_text {str} -- _the plain text value to check_
            hashed_text {str} -- _the hashed value_

        Returns:
            bool -- _whether the values match_
        '''
        return cls.hash_context.verify(plain_text, hashed_text)

    @classmethod
    def sign(cls, value: str) -> str:
        '''creates a digital signature from the server for a value

        Arguments:
            value {str} -- _value to sign_

        Returns:
            str -- _the signed string_
        '''
        signature_salt = settings.get_secret_settings().signature_salt
        return cls.serializer.dumps(value, salt=signature_salt)

    @classmethod
    def unsign(cls, value: str, max_age: int) -> str:
        '''Unsigns a value that was signed by the server

        Arguments:
            value {str} -- _the value to unsign_
            max_age {int} -- _the max age_

        Returns:
            str -- _the loaded string_
        '''
        signature_salt = settings.get_secret_settings().signature_salt
        return cls.serializer.loads(
            value,
            salt=signature_salt,
            max_age=max_age
        )
