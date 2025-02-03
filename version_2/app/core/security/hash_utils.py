from passlib.context import CryptContext

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto" 
)

def hash_password(password: str) -> str:
    '''_summary_
    hashes the password
    Arguments:
        password {str}
    Returns:
        str - the hash of the password 
    '''
    return _pwd_context.hash(password)

def check_password(plain_password: str, password_hash: str) -> bool:
    '''_summary_
    checks if the plain text password matches the hash
    Returns:
        bool 
    '''
    return _pwd_context.verify(
        plain_password, 
        password_hash
    )        
        