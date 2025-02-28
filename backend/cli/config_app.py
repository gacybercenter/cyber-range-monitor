from logging import config
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import typer
from rich import inspect
from rich.table import Table
import yaml

from .prompts import CLIPrompts
from app import settings

config_app = typer.Typer()


def get_config_map() -> dict[str, type[BaseSettings]]:
    return settings.config_model_map()


def config_docs() -> None:
    table = Table(
        title='# Build Settings Docs #',
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
        for row_contents in docs_of(model, label):
            table.add_row(*row_contents)
    CLIPrompts.print(table)


def docs_of(config_type: BaseSettings, config_label):
    for name, field in config_type.model_fields.items():
        yield [
            config_label,
            name,
            str(field.annotation.__name__),  # type: ignore
            str(field.default) if field.default else 'None',
            field.description,
            'Yes' if field.is_required() else 'No'
        ]


def show_docs_for(config_prefix: str) -> None:
    config_type_map = get_config_map()
    config = config_type_map.get(config_prefix)
    if not config:
        CLIPrompts.error(f'Config: {config_prefix} not found.')
        raise typer.Abort()
    table = Table(
        title=f'{config_prefix} Config Docs',
        header_style='bold white',
        border_style='bright_blue',
        show_lines=True
    )

    for row in docs_of(config(), config_prefix):
        table.add_row(*row)

    CLIPrompts.print(table)


@config_app.command(help='Shows the documentation for the build settings')
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
    path = Path('configs', f'config-{label}.yml')

    if not path.exists():
        CLIPrompts.error(f'File {path} does not exist.')
        raise typer.Abort()

    CLIPrompts.info(f'Exporting {label} to config.yml')
    with open(path, 'r') as f:
        contents = yaml.safe_load(f)

    with open('config.yml', 'w') as f:
        yaml.dump(contents, f, default_flow_style=False, sort_keys=False)
    CLIPrompts.info('Export complete.')


@config_app.command(help='creates the default settings')
def builder() -> None:
    CLIPrompts.header('bold blue', 'config-yml-builder')

    choice = CLIPrompts.choice(
        'Enter a name for your yml file (without the .yml extension)',
        'config-'
    )
    file = f'{choice}.yml'
    path = Path('configs', file)
    if path.exists():
        choice = CLIPrompts.choice(
            'File already exists, do you want to overwrite it? (y/n)',
        )
        if not choice.lower().startswith('y'):
            CLIPrompts.info('Aborting.')
            return
    config_type_map = get_config_map()
    all_but_secrets = {key: value for key,
                       value in config_type_map.items() if key != 'secrets'}

    yml_contents = {}
    for label, config_type in all_but_secrets.items():
        yml_contents[label] = set_group(label, config_type())
    CLIPrompts.info(
        f'{file} created exporting under the label {file.split("-")[1]}')
    yml_contents['label'] = file.split('-')[1]
    with open(path, 'w') as f:
        yaml.dump(yml_contents, f, default_flow_style=False, sort_keys=False)
    CLIPrompts.info(
        f'export complete, type cli config set {file.split("-")[1]} to use this config')


def set_group(label: str, config: BaseSettings) -> dict:
    values = {}
    for field_name, field_info in config.model_fields.items():
        type_name = field_info.annotation.__name__ if field_info.annotation else 'N/A'
        default = field_info.default if field_info.default else 'N/A'
        docs = field_info.description if field_info.description else 'N/A'
        choice = CLIPrompts.choice(
            f'({label}) - {field_name}\n {docs} <type={type_name}> <default={default}>'
        )

        if not choice:
            choice = default
        values[field_name] = choice
        CLIPrompts.info(f'set -> {field_name}={choice}')
    return values

