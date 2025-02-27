import os
import secrets
from cryptography.fernet import Fernet
from rich.console import Console

console = Console()

def get_redis_pwd() -> str:
    choice = console.input(
        'Enter as password for redis: ',
        password=True
    )
    if choice == '' or not console.input(
        'Re-type to confirm: ',
        password=True
    ) == choice:
        console.print('Invalid password', style='bold red')
        return get_redis_pwd()
    return choice


def create_secrets() -> dict:
    console.print('Creating secrets...', style='italic green')
    return {
        'secret_key': secrets.token_urlsafe(32),
        'signature_salt': secrets.token_urlsafe(32),
        'encryption_key': Fernet.generate_key().decode(),
        'csrf_key': secrets.token_urlsafe(32),
        'redis_password': get_redis_pwd(),
    }


def write_secrets(vars: dict) -> None:
    if os.path.exists('secrets.env') and not console.input(
        'a secrets.env exists, do you want to overwrite it?]\nNOTE: You will have recreate the database. '
        '[y/n]: '
    ).lower() == 'y':
        return
    with open('secrets.env', 'w') as f:
        for key, value in vars.items():
            f.write(f'{key}={value}\n')


def main() -> None:
    secrets_dict = create_secrets()
    write_secrets(secrets_dict)


if __name__ == '__main__':
    main()
