from passlib.context import CryptContext
import bcrypt
from hmac import compare_digest


_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_pwd(plain_pwd: str) -> str:
    '''
    hashes the plain password -> scheme=bcrypt

    Arguments:
        plain_pwd {str} 

    Returns:
       str -- the hashed passowrd
    '''
    global _pwd_context
    return _pwd_context.hash(plain_pwd)


def check_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    '''
    checks if the plain password matches the hashed password

    Arguments:
        plain_pwd {str} -- the plain password; not hashed
        hashed_pwd {str} -- the users password hash 

    Returns:
        bool 
    '''
    global _pwd_context
    result = _pwd_context.verify(plain_pwd, hashed_pwd)
    return compare_digest(str(result), str(True))
