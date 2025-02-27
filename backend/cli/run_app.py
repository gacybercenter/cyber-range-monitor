import typer
import os
import subprocess

from .prompts import CLIPrompts


run_app = typer.Typer()


@run_app.command()
def dev(
    environment: str = typer.Option(
        'dev', help='The environment to run the app in')
) -> None:
    os.environ['ENVIRONMENT'] = environment
    CLIPrompts.info('Starting running API in Dev mode...')
    subprocess.run(['fastapi', 'dev', 'main.py'])


@run_app.command()
def prod() -> None:
    subprocess.run(['fastapi', 'run', 'main.py',
                   '--port', '8000', '--host', '0.0.0.0'])


@run_app.command()
def run_container() -> None:
    cmd = os.getenv('APP_ENV', 'dev')
    CLIPrompts.info(f'APP_ENV={cmd}')
    if cmd != 'dev':
        cmd = 'run'
    CLIPrompts.info(f'CMD={cmd}')
    subprocess.run(
        ['uv', 'run', 'fastapi', 'main.py', '--port', '8000', '--host', '0.0.0.0']
    )
