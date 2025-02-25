import typer
import os
import subprocess

from .prompts import CLIPrompts


run_app = typer.Typer()


@run_app.command()
def dev(
    environment: str = typer.Option('dev', help='The environment to run the app in')
) -> None:
    os.environ['ENVIRONMENT'] = environment
    CLIPrompts.info('Starting running API in Dev mode...')
    subprocess.run(['fastapi', 'dev', 'main.py'])

@run_app.command()
def prod(
    environment: str = typer.Option('prod', help='The environment to run the app in')
) -> None:
    os.environ['ENVIRONMENT'] = environment
    subprocess.run(['fastapi', 'run', 'main.py', '--port', '8000', '--host', '0.0.0.0'])