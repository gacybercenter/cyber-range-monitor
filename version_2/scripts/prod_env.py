from cryptography.fernet import Fernet
import secrets 
import os 


def main() -> None:
    env = {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'SIGNATURE_SALT': secrets.token_urlsafe(32),
        'ENCRYPTION_KEY': Fernet.generate_key().decode(),
        'CSRF_SECRET_KEY': secrets.token_urlsafe(32),
        'DATABASE_URL': 'sqlite+aiosqlite:///instance/app.db'
    }
    
    for key, value in env.items():
        os.environ[key] = value

    

if __name__ == '__main__':
    main()