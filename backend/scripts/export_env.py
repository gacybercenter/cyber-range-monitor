

def get_env_dict() -> dict[str, str]:
    from cryptography.fernet import Fernet
    return {
        'FERNET_KEY': Fernet.generate_key().decode('utf-8'),
        'PBKDF2_SALT': Fernet.generate_key().decode('utf-8'),
    }
