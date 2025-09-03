"""
Security related services that are constructed once at application
startup.
"""
import base64
from dataclasses import dataclass
from typing import Any, NamedTuple, Protocol, Self

import itsdangerous
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext


class StaleCallback(Protocol):
    def __call__(self, new_hash: str) -> None: ...


@dataclass(slots=True)
class Encryptor:
    """
    Service for encrypting and decrypting messages
    """

    fernet: Fernet

    @classmethod
    def create(cls, *, key: str, salt: str, iterations: int, length: int) -> Self:
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
        return cls(fernet=fernet)

    def encrypt(self, message: str) -> bytes:
        return self.fernet.encrypt(message.encode())

    def decrypt(self, encrypted_message: bytes, *, ttl: int | None = None) -> str:
        return self.fernet.decrypt(encrypted_message, ttl=ttl).decode()


@dataclass(slots=True)
class PasswordHashes:
    """
    Service for hashing and verifying passwords
    using bcrypt with pepper.
    """

    crypt_context: CryptContext
    pepper: str

    def _pepper_str(self, message: str) -> str:
        return f'{message}{self.pepper}'

    def hash_password(self, password: str) -> str:
        """
        Hashes the provided password using bcrypt with an optional pepper.

        Parameters
        ----------
        password : str

        Returns
        -------
        str

        Raises
        ------
        RuntimeError
            _Package missing, shouldn't happen_
        """
        message = self._pepper_str(password)
        try:
            hashed = self.crypt_context.hash(message)
        except Exception as e:
            raise RuntimeError(
                'bcrypt backend not available, meaning it is not installed.'
            ) from e

        return hashed

    def check_password(
        self,
        *,
        plaintext: str,
        stored_hash: str,
        on_stale: StaleCallback | None = None,
    ) -> bool:
        """
        Verifies a plain password against the stored hash. If the hash is stale,

        Parameters
        ----------
        plain_password : str
        stored_hash : str
        on_stale : StaleCallback | None, optional
            _How to handle stale passwords_, by default None

        Returns
        -------
        bool
            _password hashes match_

        """
        message = self._pepper_str(plaintext)
        try:
            okay = self.crypt_context.verify(message, stored_hash)
        except Exception:
            return False

        if okay and on_stale and self.crypt_context.needs_update(stored_hash):
            on_stale(self.hash_password(plaintext))

        return okay

    def needs_rehash(self, stored_hash: str) -> bool:
        return self.crypt_context.needs_update(stored_hash)


class TimestampedMessage(NamedTuple):
    message: str
    timestamp: float

@dataclass(slots=True)
class SignatureProvider:
    """
    Service for signing and verifying signed messages
    using itsdangerous URLSafeSerializer and msgspec for
    serialization.
    """

    signer: itsdangerous.URLSafeTimedSerializer

    def sign_message(self, plaintext: str) -> str:
        return self.signer.dumps(plaintext)


    def _load(
        self,
        message: str,
        max_age: int | None,
        return_timestamp: bool
    ) -> Any | None:
        try:
            return self.signer.loads(
                message,
                max_age=max_age,
                return_timestamp=return_timestamp
            )
        except (
            itsdangerous.BadTimeSignature,
            itsdangerous.BadSignature,
            itsdangerous.SignatureExpired
        ):
            return None

    def get_message(
        self,
        signed_message: str,
        *,
        max_age: int | None = None,
    ) -> str | None:
        '''
        Loads and verifies a signed message.

        Parameters
        ----------
        signed_message : str
        max_age : int | None, optional
            _max age of a signed message_, by default None

        Returns
        -------
        str | None
            _The message or none if the signature is invalid_
        '''
        return self._load(signed_message, max_age=max_age, return_timestamp=False)

    def get_timestamped_message(
        self,
        signed_message: str,
        *,
        max_age: int | None = None,
    ) -> TimestampedMessage | None:
        '''
        Loads and verifies a signed message and returns
        a TimestampedMessage.

        Parameters
        ----------
        signed_message : str
            _the signed message_
        max_age : int | None, optional
            _the max age of the message_, by default None

        Returns
        -------
        TimestampedMessage | None
        '''
        result = self._load(
            signed_message,
            max_age=max_age,
            return_timestamp=True
        )
        if result is None:
            return None
        return TimestampedMessage(*result)