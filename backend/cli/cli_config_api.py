from cProfile import label
from pathlib import Path
from re import A
from typing import Optional

from annotated_types import T
from pydantic_settings import BaseSettings
import typer
import yaml
from rich import inspect
from rich.table import Table

from app import config
from app.core.settings.base import SettingsMixin

from . import cli_console

config_app = typer.Typer()


DOCS_CMD_HELP = (
    'Displays a table of the documentation for the config.yml '
    'and accepts an optional group to show. \n\t[usage: docs | docs <group>]'
    '\n\t[example: docs | docs api_key]'
)

DOCS_GROUP_OPT_HELP = (
    'the config group to show the documentation for '
    '[example: "docs api_key" shows the api_key config documentation]'
)

SET_CMD_HELP = (
    'given a label for a config.<label>.yml file in the "configs" directory (e.g config.dev.yml, label=dev),'
    'it sets it as the current config the API will run on by exporting its contents to the config.yml file.'
    '\n\t[usage: set <label>]'
    '\n\t[example: set dev] -> config.yml will be set to the contents of config.dev.yml'
)

SET_LABEL_OPT_HELP = (
    'the label for the yml file (e.g set dev -> config.yml = config.dev.yml)'
)

SHOW_CMD_HELP = (
    'Displays the current config.yml file in the CLI console in a yml-like format.'
    '\n\t[usage: show]'
)

GROUPS_CMD_HELP = (
    'Displays the names of the groups / sections in the yml file to use with the CLI.'
    '\n\t[usage: groups]'
)

REFRESH_CMD_HELP = (
    'Refreshes the current config.yml file by re-exporting the contents of the config.<label>.yml file'
)


def get_config_map() -> dict[str, type[BaseSettings]]:
    return config.config_model_map()


class ConfigDocs:
    @staticmethod
    def table_base() -> Table:
        table = Table(
            title='# Build config Docs #',
            header_style='bold white',
            border_style='bright_blue',
            show_lines=True
        )

        table.add_column('YML Group', style='bright_blue')
        table.add_column('Property Name', style='cyan', no_wrap=True)
        table.add_column('Property Type', style='magenta')
        table.add_column('Default', style='yellow')
        table.add_column('Summary', style='green')
        table.add_column('Required', style='red', width=3)

        return table

    @staticmethod
    def add_config_group(label: str, config_type: type[SettingsMixin], table: Table) -> None:
        '''adds a config group to the table

        Arguments:
            label {str} -- the label of the group (e.g 'api_key')
            config_type {type[BaseSettings]} -- the base settings class for the group
            table {Table} -- the table to add the group to
        '''
        model = config_type()
        docs = model.get_docs(label)
        for doc in docs:
            table.add_row(*doc.to_row())

    @staticmethod
    def config_preview() -> None:
        '''previews the config.yml file in the CLI console in a yml like format
        '''
        yml = config.get_config_yml()
        for group_name in yml.model_fields.keys():
            cli_console.print_stdout(f'\n[bold blue]{group_name}[/bold blue]')
            group_model: SettingsMixin = getattr(yml, group_name)
            ConfigDocs.stringify_group(group_model, group_name)

    @staticmethod
    def stringify_group(group_model: SettingsMixin, group_name: str) -> None:
        model_dump = group_model.model_dump()
        group_docs = group_model.get_docs(group_name)
        required = '[bold red](required)[/bold red]'
        optional = '[italic yellow](optional)[/italic yellow]'
        for doc in group_docs:
            require_str = required if doc.required == 'Yes' else optional
            val = model_dump.get(doc.name)
            attr_str = (
                f'\t[italic green]{doc.name}[/italic green]: '
                f'[bold white]{val}[/bold white]'
                f'// {require_str}, [cyan]{doc.type_name}[/cyan]'
            )
            cli_console.print_stdout(attr_str)


@config_app.command(help=DOCS_CMD_HELP)
def docs(
    group: Optional[str] = typer.Argument(None, help=DOCS_GROUP_OPT_HELP)
) -> None:
    table = ConfigDocs.table_base()
    config_type_map = get_config_map()
    for label, config_type in config_type_map.items():
        if group and not group.lower().startswith(label.lower()):
            continue
        ConfigDocs.add_config_group(label, config_type, table) # type: ignore

    cli_console.print_stdout(table)


@config_app.command(help=SHOW_CMD_HELP)
def show() -> None:
    ConfigDocs.config_preview()
    
    
    

@config_app.command(help='shows the names of the groups / sections in the yml file to use with the CLI')
def groups() -> None:
    config_type_map = get_config_map()
    cli_console.print_stdout(
        '[blue]YML Config Groups: [/blue]\n'
        f'[italic green]{', '.join(config_type_map.keys())}[/italic green]\n'
    )


def resolve_label_path(label: str) -> Path:
    path = Path('configs', f'config.{label}.yml')
    if not path.exists():
        cli_console.error(f'File {path} does not exist.')
        raise typer.Abort()
    return path



def load_yml(path: Path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def export_yml(path: str, contents: dict) -> None:
    with open(path, 'w') as f:
        yaml.dump(contents, f, default_flow_style=False, sort_keys=False)

@config_app.command(help=SET_CMD_HELP)
def set(
    label: str = typer.Argument(
        ..., 
        help=SET_LABEL_OPT_HELP
    )
) -> None:
    cli_console.header('bold blue', 'config-yml-setter')
    path = resolve_label_path(label)
    cli_console.info(f'Exporting {label} to config.yml')
    contents = load_yml(path)
    export_yml('config.yml', contents)
    cli_console.info('Export complete.')

@config_app.command(help=REFRESH_CMD_HELP)
def refresh() -> None:
    current_config = load_yml(Path('config.yml'))
    config_label = current_config['app'].get('config_label')
    if not config_label:
        cli_console.error('No config_label found in config.yml')
        raise typer.Abort()
    
    path = resolve_label_path(config_label)
    updated_config = load_yml(path)
    
    export_yml('config.yml', updated_config)
    
    cli_console.info(f'Config "{config_label}" refreshed.')
    