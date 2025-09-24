

import unicodedata
from typing import Protocol

from starlette.concurrency import run_in_threadpool

from range_monitor.security import PasswordPolicy


class OnStaleCallback(Protocol):
    async def __call__(self, new_hash: str) -> None: ...

class PasswordService:

    def __init__(self, policy: PasswordPolicy) -> None:
        self._policy: PasswordPolicy = policy

    def _hash_password_sync(self, password: str) -> str:
        '''
        Hashes a password using the defined password policy.

        Parameters
        ----------
        password : str
            _The plain password to hash_

        Returns
        -------
        str
            _The hashed password_
        '''

        message = unicodedata.normalize('NFC', password).encode('utf-8')
        peppered_message = self._policy.compute_pepper(message)
        return self._policy.bcrypt.hash(peppered_message)

    async def hash_password(self, password: str) -> str:
        return await run_in_threadpool(self._hash_password_sync, password)

    def _verify_password_sync(
        self,
        *,
        plaintext: str,
        stored_hash: str,
    ) -> bool:
        '''
        Verifies a plain password against the stored hash.

        Parameters
        ----------
        plaintext : str
        stored_hash : str

        Returns
        -------
        bool
        '''
        message = unicodedata.normalize('NFC', plaintext).encode('utf-8')
        peppered_message = self._policy.compute_pepper(message)
        return self._policy.bcrypt.verify(peppered_message, stored_hash)

    async def verify_password(
        self,
        *,
        plaintext: str,
        stored_hash: str,
    ) -> bool:
        return await run_in_threadpool(
            self._verify_password_sync,
            plaintext=plaintext,
            stored_hash=stored_hash,
        )

    async def is_hash_stale(self, stored_hash: str) -> bool:
        '''
        Checks if the provided hash is considered stale by the current policy.

        Parameters
        ----------
        stored_hash : str

        Returns
        -------
        bool
            _True if the hash is stale and should be re-hashed_
        '''
        return await run_in_threadpool(
            self._policy.bcrypt.needs_update,
            stored_hash
        )