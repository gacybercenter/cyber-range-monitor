import os
import secrets
from cryptography.fernet import Fernet
from rich.console import Console
import app
from app.config import Settings, running_config
from .utils import script_hdr

def create_secrets() -> dict:
    return {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'SIGNATURE_SALT': secrets.token_urlsafe(32),
        'ENCRYPTION_KEY': Fernet.generate_key().decode(),
        'CSRF_SECRET_KEY': secrets.token_urlsafe(32),
        'DATABASE_URL': 'sqlite+aiosqlite:///instance/app.db',
        'REDIS_PASSWORD': input('REDIS_PASSWORD= ')
    }


def write_secrets(env: str, vars: dict) -> None:
    with open(f'instance/.{env}.env', 'w') as f:
        for key, value in vars.items():
            f.write(f'{key}={value}\n')


def create_defaults(console: Console) -> None:
    for app_env in ('prod', 'dev'):
        create_env(console, app_env, prompt_for_complete=False)


def create_env(
    console: Console,
    app_env: str,
    prompt_for_complete: bool = False
) -> None:
    prompt = (
        '[italic green]A "complete" config will store the entire config model[/italic green]'
        '[italic white]Store complete config (type YES): [/italic] '
    )
    env_secrets = create_secrets()
    write_secrets(app_env, env_secrets)
    if prompt_for_complete and console.input(prompt) != 'YES':
        return

    os.environ['APP_ENV'] = app_env
    Settings.load()
    full_env_config = running_config()
    write_secrets(app_env, full_env_config.model_dump())


def main(
    console: Console,
    do_default: bool = False,
    app_env: str = 'dev'
) -> None:
    script_hdr(console, 'env_setup.py', 'bold blue')
    if do_default:
        create_defaults(console)
        console.print(
            '[bold green]APP_ENV(s) prod and dev created.[/bold green]')
        return
    else:
        create_env(console, app_env, True)
        console.print(f'[bold green]APP_ENV {app_env} created.[/bold green]')
        return


if __name__ == '__main__':
    main(Console(), do_default=True)
