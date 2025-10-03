import hashlib
import hmac
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_secret_key(length: int = 32) -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_fernet_key() -> str:
    return Fernet.generate_key().decode('utf-8')


def get_derived_key(
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


def get_pepper(
    message: bytes,
    pepper: bytes
) -> bytes:
    '''
    Computes a peppered message by hashing the message with the pepper.

    Parameters
    ----------
    message : bytes
        The message to be peppered.
    pepper : bytes
        The pepper to use for hashing.

    Returns
    -------
    bytes
        The peppered message.
    '''
    return hmac.new(pepper, message, hashlib.sha256).digest()