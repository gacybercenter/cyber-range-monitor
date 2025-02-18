import os
import secrets
from cryptography.fernet import Fernet


def create_secrets_dict() -> dict:
    return {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'SIGNATURE_SALT': secrets.token_urlsafe(32),
        'ENCRYPTION_KEY': Fernet.generate_key().decode(),
        'CSRF_SECRET_KEY': secrets.token_urlsafe(32),
        'DATABASE_URL': 'sqlite+aiosqlite:///instance/app.db',
        'REDIS_PASSWORD': input('REDIS_PASSWORD= ')
    }


def create_env(app_env) -> None:
    with open(f'.{app_env}.env', 'w') as f:
        for key, value in create_secrets_dict().items():
            f.write(f'{key}={value}\n')


def main() -> None:
    print('<< ~api\\scripts\\key_gen.py~ >>')
    app_env = os.getenv("APP_ENV", 'dev')
    print(f'<< APP_ENV={app_env} >>')
    create_env(app_env)


if __name__ == '__main__':
    main()
