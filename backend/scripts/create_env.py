import secrets
from cryptography.fernet import Fernet


def create_secrets(app_env) -> dict:
    return {
        'ENVIRONMENT': app_env,
        'SECRET_KEY': secrets.token_urlsafe(32),
        'SECRET_SIGNATURE_SALT': secrets.token_urlsafe(32),
        'SECRET_ENCRYPTION_KEY': Fernet.generate_key().decode(),
        'SECRET_CSRF_KEY': secrets.token_urlsafe(32),
        'DATABASE_URL': 'sqlite+aiosqlite:///instance/app.db',
        'REDIS_PASSWORD': input('REDIS_PASSWORD='),
    }


def write_secrets(env: str, vars: dict) -> None:
    with open(f'{env}.env', 'w') as f:
        for key, value in vars.items():
            f.write(f'{key}={value}\n')


def create_defaults() -> None:
    for app_env in ('prod', 'dev'):
        create_env(app_env)


def create_env(
    app_env: str
) -> None:
    env_secrets = create_secrets(app_env)
    write_secrets(app_env, env_secrets)


def main() -> None:
    create_defaults()


if __name__ == '__main__':
    main()
