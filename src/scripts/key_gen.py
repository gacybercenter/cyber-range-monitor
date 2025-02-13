import secrets
import os
from cryptography.fernet import Fernet


def create_secrets_dict() -> dict:
    return {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'SIGNATURE_SALT': secrets.token_urlsafe(32),
        'ENCRYPTION_KEY': Fernet.generate_key().decode(),
        'CSRF_SECRET_KEY': secrets.token_urlsafe(32),
        'DATABASE_URL': 'sqlite+aiosqlite:///instance/app.db'
    }



def create_dev_env() -> None:
    env = create_secrets_dict()
    with open('.env', 'w') as f:
        for key, value in env.items():
            f.write(f'{key}={value}\n')
    
def create_prod_env(secrets_dir: str = 'secrets') -> None:
    os.makedirs(secrets_dir, exist_ok=True)
    secret_dict = create_secrets_dict()
    for key, value in secret_dict.items():
        secret_path = os.path.join(secrets_dir, key)
        with open(secret_path, 'w') as f:
            f.write(value)
    

def main() -> None:
    create_env()

if __name__ == '__main__':
    main()
