import typer
import os
import subprocess
import asyncio

from scripts.prompts import CLIPrompts

run_app = typer.Typer()
docker_app = typer.Typer()


@docker_app.command(help='builds the application')
def build(
    mode: str = typer.Option(
        'dev',
        '--mode',
        '-m',
        help='the mode or environment to build the application for specifying the env file to use'
    )
) -> None:
    env_file = f'.{mode}.env'
    if not os.path.exists(env_file):
        CLIPrompts.error(
            f'[red]Error: [/red] Unknown APP_ENV: Could not find file  .{mode}.env at: {env_file}')
        raise typer.Abort()
    CLIPrompts.info(f'[green]Building environment...[/green]')
    subprocess.run(['docker', 'compose', '--env-file', env_file, 'build'])


@docker_app.command(help='docker compose up')
def up(
    mode: str = typer.Option(
        'dev',
        '--mode',
        '-m',
        help='the mode or environment to build the application for specifying the env file to use'
    )
) -> None:
    env_file = f'.{mode}.env'
    if not os.path.exists(env_file):
        CLIPrompts.error(
            f'Unknown APP_ENV: Could not find file  .{mode}.env at: {env_file}')
        raise typer.Abort()
    CLIPrompts.info(f'[green]Runng docker compose up....[/green]')
    subprocess.run(['docker', 'compose', '--env-file', env_file, 'up'])


@docker_app.command(help='the entrypoint for docker')
def begin_api() -> None:
    app_env = os.getenv('APP_ENV', 'not-set')
    if app_env == 'not-set':
        CLIPrompts.warn(
            'the APP_ENV was not set and is defaulting to "dev" mode.'
        )
        app_env = 'dev'

    from scripts.seed_db import run

    asyncio.run(run())

    mode = 'run' if app_env == 'prod' else 'dev'
    command = f'fastapi {mode} app.main --reload --host 0.0.0.0'
    CLIPrompts.info(f'COMMAND={command}')
    subprocess.run(command.split(' '))


@run_app.command(help='runs the application in dev mode')
def dev() -> None:
    CLIPrompts.info(
        f'[green]Running Application in dev mode using APP_ENV={os.getenv('APP_ENV', 'not-set')}[/green]'
    )
    subprocess.run(['fastapi', 'dev', 'run.py'])
