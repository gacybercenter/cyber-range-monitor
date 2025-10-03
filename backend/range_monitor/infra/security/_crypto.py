import dataclasses as dc
import hashlib
import hmac
import unicodedata

from range_monitor.infra.security._policy import CryptoPolicy


def norm_encode(plaintext: str) -> bytes:
    return unicodedata.normalize('NFC', plaintext).encode('utf-8')

def pepper_msg(msg: bytes, pepper: bytes) -> bytes:
    return hmac.new(pepper, msg, hashlib.sha256).digest()

@dc.dataclass(slots=True)
class CryptoService:
    policy: CryptoPolicy

    def pepper_password(self, message: bytes) -> bytes:
        return pepper_msg(message, self.policy.bcrypt_pepper)


    def hash_password(self, password: str) -> str:
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

        peppered_bytes = self.pepper_password(norm_encode(password))
        return self.policy.bcrypt.hash(peppered_bytes)

    def verify_password(self, *, plain: str, hashed: str) -> bool:
        '''
        Verifies a plain password against a hashed password.

        Parameters
        ----------
        plain : str
            _The plain password to verify_
        hashed : str
            _The hashed password to verify against_

        Returns
        -------
        bool
            _True if the password matches, False otherwise_
        '''

        peppered_bytes = self.pepper_password(norm_encode(plain))
        return self.policy.bcrypt.verify(peppered_bytes, hashed)


    def is_hash_stale(self, hashed: str) -> bool:
        return self.policy.bcrypt.needs_update(hashed)


    def encrypt_text(self, plaintext: str) -> bytes:
        return self.policy.fernet.encrypt(norm_encode(plaintext))


    def decrypt_bytes(self, cipher_bytes: bytes) -> str:
        return self.policy.fernet.decrypt(cipher_bytes).decode('utf-8')