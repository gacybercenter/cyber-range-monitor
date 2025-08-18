from typing import Protocol

from passlib.context import CryptContext
from passlib.exc import MissingBackendError
from app.core.singletons import SingletonMeta
from .settings import get_crypto_settings


class StaleCallback(Protocol):
    def __call__(self, new_hash: str) -> None: ...


def create_crypt_ctx(
    rounds: int = 12,
) -> CryptContext:
    return CryptContext(
        schemes=['bcrypt_sha256'],
        deprecated='auto',
    )


class PasswordManager(metaclass=SingletonMeta):
    crypt_ctx: CryptContext = create_crypt_ctx()
    _pepper: str = get_crypto_settings().BCRYPT_PEPPER

    def pepper(self, password: str) -> str:
        """
        Applies a pepper to the password before hashing.

        Parameters
        ----------
        password : str

        Returns
        -------
        str
            The password with the pepper applied.
        """
        return f'{password}{self._pepper}'

    def hash_password(self, password: str) -> str:
        """
        Hashes the provided password using bcrypt with an optional pepper.

        Parameters
        ----------
        password : str

        Returns
        -------
        str
            The hashed password.
        """
        peppered = self.pepper(password)
        try:
            return self.crypt_ctx.hash(peppered)
        except MissingBackendError as e:
            raise RuntimeError(
                'bcrypt backend not available, meaning it is not installed.'
            ) from e

    def check_password(
        self,
        *,
        plain_password: str,
        stored_hash: str,
        on_stale: StaleCallback | None = None,
    ) -> bool:
        """
        Verifies a plain password against the stored hash. If the hash is stale,
        it can be updated using the provided callback.

        Parameters
        ----------
        plain_password : str
        stored_hash : str
        on_stale : StaleCallback | None, optional
            How to handle stale passwords, by default None

        Returns
        -------
        bool
            True if the password hashes match, False otherwise.
        """
        peppered = self.pepper(plain_password)
        try:
            is_valid = self.crypt_ctx.verify(peppered, stored_hash)
        except MissingBackendError:
            raise RuntimeError(
                'bcrypt backend is not available, meaning it is not installed.'
            )

        if is_valid and self.crypt_ctx.needs_update(stored_hash):
            new_hash = self.crypt_ctx.hash(peppered)
            if on_stale:
                on_stale(new_hash)

        return is_valid

