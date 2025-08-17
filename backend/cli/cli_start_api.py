import subprocess

import typer
import yaml

from . import cli_console

run_app = typer.Typer()


@run_app.command()
def dev() -> None:
    cli_console.info('Starting running API in Dev mode...')
    subprocess.run(['fastapi', 'dev', 'main.py'])


@run_app.command()
def prod() -> None:
    subprocess.run(['fastapi', 'run', 'main.py', '--port', '8000', '--host', '0.0.0.0'])
