from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from .const import SECRET_CONFIG

_fernet = Fernet(SECRET_CONFIG.encryption_key.encode())
_serializer = URLSafeTimedSerializer(
    SECRET_CONFIG.secret_key, salt=SECRET_CONFIG.signature_salt
)


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """hashes the password

    Arguments:
        password {str}
    Returns:
        str - the hash of the password
    """
    return _pwd_context.hash(password)


def check_password(plain_password: str, password_hash: str) -> bool:
    """checks if the plain text password matches the hash
    Returns:
        bool
    """
    return _pwd_context.verify(plain_password, password_hash)


def encrypt_data(data: str) -> str:
    """encrypts a string with the fernet key
    Arguments:
        data {str} -- the data to encrypt

    Returns:
        str -- the encrypted data
    """
    return _fernet.encrypt(data.encode()).decode()


def decrypt_data(data: str) -> str:
    """decrypts a string with the fernet key

    Arguments:
        data {str} -- the data to decrypt

    Returns:
        str -- the decrypted data
    """
    return _fernet.decrypt(data.encode()).decode()


def create_signature(data: str) -> str:
    """uses the URLSafeTimedSerializer to create a signature
    Arguments:
        data {str} -- the data to sign
    Returns:
        str -- the signed data
    """
    return _serializer.dumps(data)


def load_signature(token: str, max_age: int | None = None) -> str:
    """Loads a signature from a signed token issued from the server
    Arguments:
        token {str} -- a token that has been signed

    Keyword Arguments:
        max_age {Optional[int]} -- the maximum age of the token in seconds (default: {None})

    Raises:
        SignatureExpired: if the token is expired
        BadSignature: if the token is invalid
    Returns:
        Optional[str] -- the signature if the token is valid, otherwise None
    """
    return _serializer.loads(token, max_age=max_age)
