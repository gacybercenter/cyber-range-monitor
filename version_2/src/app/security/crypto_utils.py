from passlib.context import CryptContext
from typing import Optional
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from app.config import running_config

settings = running_config()


_fernet = Fernet(settings.ENCRYPTION_KEY.encode())
_serializer = URLSafeTimedSerializer(   
    settings.SECRET_KEY,
    salt=settings.SIGNATURE_SALT
)


_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    '''hashes the password
    
    Arguments:
        password {str}
    Returns:
        str - the hash of the password 
    '''
    return _pwd_context.hash(password)


def check_password(plain_password: str, password_hash: str) -> bool:
    '''checks if the plain text password matches the hash
    Returns:
        bool 
    '''
    return _pwd_context.verify(
        plain_password,
        password_hash
    )

def encrypt_data(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt_data(data: str) -> str:
    return _fernet.decrypt(data.encode()).decode()


def create_signature(data: str) -> str:
    return _serializer.dumps(data)


def load_signature(token: str, max_age: Optional[int] = None) -> Optional[str]:
    '''_summary_
    Loads a signature from a signed token issued from the server 
    Arguments:
        token {str} -- a token that has been signed 

    Keyword Arguments:
        max_age {Optional[int]} -- the maximum age of the token in seconds (default: {None})

    Raises:
        SignatureExpired: if the token is expired
        BadSignature: if the token is invalid
    Returns:
        Optional[str] -- the signature if the token is valid, otherwise None
    '''
    return _serializer.loads(token, max_age=max_age)
