from pathlib import Path
from typing import Optional

import typer
import yaml


from . import cli_console

config_app = typer.Typer()

SET_CMD_HELP = (
    'given a label for a config.<label>.yml file in the "configs" directory (e.g config.dev.yml, label=dev),'
    'it sets it as the current config the API will run on by exporting its contents to the config.yml file.'
    '\n\t[usage: set <label>]'
    '\n\t[example: set dev] -> config.yml will be set to the contents of config.dev.yml'
)

SET_LABEL_OPT_HELP = (
    'the label for the yml file (e.g set dev -> config.yml = config.dev.yml)'
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
def set(label: str = typer.Argument(..., help=SET_LABEL_OPT_HELP)) -> None:
    cli_console.header('bold blue', 'config-yml-setter')
    path = resolve_label_path(label)
    cli_console.info(f'Exporting {label} to config.yaml')
    contents = load_yml(path)
    export_yml('app.config.yaml', contents)
    cli_console.info('Export complete.')
