import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.singletons import SingletonMeta

from .settings import get_crypto_settings


def _create_fernet() -> Fernet:
    crypto_settings = get_crypto_settings()
    encoded_enc_salt = crypto_settings.ENCRYPTION_SALT.encode('utf-8')
    key_bytes = crypto_settings.ENCRYPTION_KEY.encode('utf-8')
    pdkdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=crypto_settings.PBKDF2_KEY_LENGTH,
        salt=encoded_enc_salt,
        iterations=crypto_settings.PBKDF2_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(pdkdf.derive(key_bytes))
    return Fernet(key)

class Encryptor(metaclass=SingletonMeta):
    fernet: Fernet = _create_fernet()

    def encrypt_to_bytes(self, input_str: str) -> bytes:
        return self.fernet.encrypt(input_str.encode('utf-8'))

    def decrypt_to_bytes(self, input_str: str, *, ttl: int | None = None) -> bytes:
        return self.fernet.decrypt(input_str.encode('utf-8'), ttl=ttl)

    def encrypt_string(self, input_str: str) -> str:
        return self.encrypt_to_bytes(input_str).decode('utf-8')

    def decrypt_string(self, input_str: str, *, ttl: int | None = None) -> str:
        return self.decrypt_to_bytes(input_str, ttl=ttl).decode('utf-8')