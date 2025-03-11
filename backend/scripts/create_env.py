import os
import secrets

from cryptography.fernet import Fernet
from rich.console import Console

console = Console()


def get_redis_pwd() -> str:
    choice = console.input("Enter as password for redis: ", password=True)
    if not choice or choice == '':
        console.print(
            '[bold red] Password cannot be empty. [/bold red],'
            ' Try again. '
        )
        return get_redis_pwd()
    return choice


def create_secrets() -> dict:
    return {
        "secret_key": secrets.token_urlsafe(32),
        "signature_salt": secrets.token_urlsafe(32),
        "encryption_key": Fernet.generate_key().decode(),
        "csrf_key": secrets.token_urlsafe(32),
        "redis_password": get_redis_pwd(),
    }


def confirm_overwrite() -> bool:
    prompt = (
        "a .env file already exists, do you want to overwrite it?"
        "\n[bold red] NOTE: [/bold red] You will have to recreate the database due different encryption keys. "
        "[y/n]: "
    )
    choice = console.input(prompt).lower().strip()
    return choice is not None and choice[0] == 'y'


def write_secrets(vars: dict, path: str = '.env') -> None:
    if os.path.exists(".env") and not confirm_overwrite():
        console.print('Exiting...')
        return

    with open(path, "w") as f:
        for key, value in vars.items():
            f.write(f"{key}={value}\n")


def main() -> None:
    secrets_dict = create_secrets()
    console.print('Writing secrets to .env file in backend...')
    write_secrets(secrets_dict)
    console.print('Copying secrets to project root...')
    write_secrets(secrets_dict, '../.env')
    console.print(
        '[italic green] script complete and secrets written to .env [/italic green]')


if __name__ == "__main__":
    main()
