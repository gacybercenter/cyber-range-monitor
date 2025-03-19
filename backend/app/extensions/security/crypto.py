import json

from cryptography.fernet import Fernet

from itsdangerous import URLSafeTimedSerializer

from passlib.context import CryptContext

from app import config



secrets_config = config.get_secrets()

_fernet = Fernet(secrets_config.encryption_key.encode())
_serializer = URLSafeTimedSerializer(
    secrets_config.secret_key, 
    salt=secrets_config.signature_salt
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

def hash_dict(dict_hashed: dict) -> str:
    json_str = json.dumps(dict_hashed, sort_keys=True)
    return _pwd_context.hash(json_str)
    
def compare_dict_hashes(dict_1: dict, dict_2: dict) -> bool:
    '''Compares two dictionaries to see if they are the same

    Arguments:
        dict_1 {dict} -- the first dictionary
        dict_2 {dict} -- the second dictionary

    Returns:
        bool -- whether the dictionaries are the same
    '''
    return _pwd_context.verify(hash_dict(dict_1), hash_dict(dict_2))


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



