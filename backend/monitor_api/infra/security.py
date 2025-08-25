"""
Security related services that are constructed once at application
startup.
"""
import base64
from collections.abc import Callable
from dataclasses import dataclass
from typing import Self, TypeAlias

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext


@dataclass(slots=True)
class EncryptionService:
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

    def encrypt(self, message: str) -> str:
        return self.fernet.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message: str, *, ttl: int | None = None) -> str:
        return self.fernet.decrypt(encrypted_message.encode(), ttl=ttl).decode()


StaleCallback: TypeAlias = Callable[[str], None]


@dataclass(slots=True)
class PasswordService:
    """
    Service for hashing and verifying passwords
    using bcrypt with pepper.
    """

    _crypt_context: CryptContext
    _pepper: str

    @classmethod
    def create(cls, *, bcrypt_pepper: str) -> Self:
        context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return cls(_crypt_context=context, _pepper=bcrypt_pepper)

    def _pepper_str(self, message: str) -> str:
        return f'{message}{self._pepper}'

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
            hashed = self._crypt_context.hash(message)
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
            okay = self._crypt_context.verify(message, stored_hash)
        except Exception:
            return False

        if okay and on_stale and self.needs_rehash(stored_hash):
            new_hash = self.hash_password(plaintext)
            on_stale(new_hash)

        return okay

    def needs_rehash(self, stored_hash: str) -> bool:
        return self._crypt_context.needs_update(stored_hash)


@dataclass(slots=True)
class SignatureService:
    """
    Service for signing and verifying signed messages
    using itsdangerous URLSafeSerializer.
    """

    _serializer: URLSafeSerializer
    _salt: str

    @classmethod
    def create(cls, *, secret_key: str, salt: str) -> Self:
        serializer = URLSafeSerializer(
            secret_key=secret_key,
            salt=salt,
        )
        return cls(_serializer=serializer, _salt=salt)

    def sign(self, message: str) -> str:
        """
        Signs a message with a salt.

        Parameters
        ----------
        message : str

        Returns
        -------
        str
        """
        return self._serializer.dumps(message, salt=self._salt)

    def load_signed(
        self, signed_message: str, *, max_age: int | None = None
    ) -> str | None:
        """
        Loads a signed message, verifying its signature and
        optional max age.

        Parameters
        ----------
        signed_message : str
        max_age : int | None, optional
            _The max allowed age of the signature_, by default None

        Returns
        -------
        str | None
            _The unsigned string_
        """
        try:
            return self._serializer.loads(
                signed_message,
                salt=self._salt,
                max_age=max_age
            )
        except Exception:
            return None
