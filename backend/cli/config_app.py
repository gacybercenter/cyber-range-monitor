from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
import typer
from app.schemas.config import SettingsMixin
import yaml
from rich import inspect
from rich.table import Table

from app import config

from .prompts import CLIPrompts

config_app = typer.Typer()


def get_config_map() -> dict[str, type[BaseSettings]]:
    return config.config_model_map()


def config_docs() -> None:
    table = Table(
        title='# Build config Docs #',
        header_style='bold white',
        border_style='bright_blue',
        show_lines=True
    )

    table.add_column(
        'Env Prefix',
        style='bright_blue'
    )
    table.add_column('Property Name', style='cyan', no_wrap=True)
    table.add_column('Property Type', style='magenta')
    table.add_column('Default', style='yellow')
    table.add_column('Summary', style='green')
    table.add_column('Required', style='red', width=3)
    config_type_map = get_config_map()
    for label, config_type in config_type_map.items():
        model = config_type()
        docs = model.get_docs(label) # type: ignore
        for doc in docs:
            table.add_row(*doc.to_row())

    CLIPrompts.print(table)


def show_docs_for(config_prefix: str) -> None:
    config_type_map = get_config_map()
    config_model = config_type_map[config_prefix]
    if not config_model:
        CLIPrompts.error(f'Config: {config_prefix} not found.')
        raise typer.Abort()
    
    table = Table(
        title=f'{config_prefix} Config Docs',
        header_style='bold white',
        border_style='bright_blue',
        show_lines=True
    )
    table.add_column('Property Name', style='cyan', no_wrap=True)
    table.add_column('Property Type', style='magenta')
    table.add_column('Default', style='yellow')
    table.add_column('Summary', style='green')
    table.add_column('Required', style='red', width=3)
    config_model = config_model() # type: ignore
    docs = config_model.get_docs(config_prefix) # type: ignore
    for doc in docs:
        table.add_row(*doc.to_row())
    CLIPrompts.print(table)


@config_app.command(help='Shows the documentation for the build config')
def docs() -> None:
    config_docs()


@config_app.command(help='inspect the current config.yml file or an optional config prefix [usage: peek | peek <prefix>]')
def peek(
    config_label: Optional[str] = typer.Option(
        None, '-p', '--prefix', help='the config prefix to peek at'
    )
) -> None:
    config_type_map = get_config_map()
    for key, value in config_type_map.items():
        if key == 'secrets' or (config_label and key != config_label):
            continue
        inspect(value(), title=key, methods=False, all=False)


@config_app.command(help='shows the available config types')
def types() -> None:
    config_type_map = get_config_map()
    CLIPrompts.print(
        '[blue]Available config types: [/blue]\n'
        f'[italic green]{', '.join(config_type_map.keys())}[/italic green]\n'
    )


@config_app.command(help='Shows the documentation for a specific config, <app, project, session, redis, secrets, database>')
def show_docs(prefix: str = typer.Argument(..., help='the config prefix to show')) -> None:
    show_docs_for(prefix)


@config_app.command(help='sets given a label for a yml file (config-dev.yml, label=dev), exports it to config.yml')
def set(
    label: str = typer.Argument(..., help='the label for the yml file')
) -> None:
    CLIPrompts.header('bold blue', 'config-yml-setter')
    path = Path('configs', f'config.{label}.yml')

    if not path.exists():
        CLIPrompts.error(f'File {path} does not exist.')
        raise typer.Abort()

    CLIPrompts.info(f'Exporting {label} to config.yml')
    with open(path, 'r') as f:
        contents = yaml.safe_load(f)

    with open('config.yml', 'w') as f:
        yaml.dump(contents, f, default_flow_style=False, sort_keys=False)
    CLIPrompts.info('Export complete.')


