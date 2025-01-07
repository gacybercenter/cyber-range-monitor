from passlib.context import CryptContext


class HashManager:
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @staticmethod
    def hash_str(plain_str: str) -> str:
        return HashManager._pwd_context.hash(plain_str)

    @staticmethod
    def check_hash(plain_str: str, hashed_str: str) -> bool:
        return HashManager._pwd_context.verify(plain_str, hashed_str)
