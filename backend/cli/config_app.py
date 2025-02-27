import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import typer
from rich import inspect
from rich.table import Table
import yaml
from scripts.create_env import create_secrets

from .prompts import CLIPrompts
from app import settings

config_app = typer.Typer()


config_type_map = settings.config_model_map()


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
    for key, value in config_type_map.items():
        if key == 'secrets' or (config_label and key != config_label):
            continue
        inspect(value(), title=key, methods=False, all=True)


@config_app.command(help='shows the available config types')
def types() -> None:
    CLIPrompts.print(
        '[blue]Available config types: [/blue]\n'
        f'[italic green]{', '.join(config_type_map.keys())}[/italic green]\n'
    )


@config_app.command(help='Shows the documentation for a specific config, <app, project, session, redis, secrets, database>')
def show_docs(prefix: str = typer.Argument(..., help='the config prefix to show')) -> None:
    show_docs_for(prefix)


@config_app.command(help='creates the default environments')
def setup() -> None:
    from scripts.create_env import main
    main()


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
        yaml.dump(contents, f)
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
    all_but_secrets = {key: value for key,
                       value in config_type_map.items() if key != 'secrets'}

    yml_contents = {}
    for label, config_type in all_but_secrets.items():
        yml_contents[label] = set_group(label, config_type())
    CLIPrompts.info(
        f'{file} created exporting under the label {file.split("-")[1]}')
    yml_contents['label'] = file.split('-')[1]
    with open(path, 'w') as f:
        yaml.dump(yml_contents, f)
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


def load_yaml(prefix: Optional[str] = None) -> dict:
    name = Path(
        'configs', f'config-{prefix}.yml') if prefix else Path('config.yml')
    if not name.exists():
        CLIPrompts.error(
            f'Cannot edit non-existent config, "{name}" does not exist.')
    with open(name, 'r') as f:
        return yaml.safe_load(f)


@config_app.command(help='opens a yml file for editing, (e.g edit dev, opens config-dev.yml)')
def edit(
    label: str = typer.Argument(
        ...,
        help='the label for the yml file (e.g label=dev edits config-dev.yml)'
    )
) -> None:
    CLIPrompts.header('bold blue', 'config-yml-editor')
    path = Path('configs', f'config-{label}.yml')
    if not path.exists():
        CLIPrompts.error(
            f'Cannot edit non-existent config, "{path}" does not exist.')
        raise typer.Abort()
    data = load_yaml(label)
    commands = ['peek', 'set', 'exit']
    CLIPrompts.clear()
    CLIPrompts.header('bold blue', 'config-yml-editor')
    CLIPrompts.info(f'Commands:{'\n'.join(commands)}')
    CLIPrompts.info(
        'Type "exit" to save and exit and help to see the commands')

    active = True
    try:
        while active:
            active = interactive_editor_loop(data, commands, label)
    except KeyboardInterrupt:
        exit_prog(label, data)
        raise typer.Abort()


def edit_help(name, desc, usage, example) -> None:
    CLIPrompts.print(
        f'[italic blue]{name}:[/italic blue]'
        f'\t\t {desc}\n'
        f'(\n\t[bold red]usage [/bold red]'
        f'[italic white]{usage}[/italic white]'
        f'\n\texample: {example})'
    )


def exit_prog(label, data) -> None:
    choice = CLIPrompts.choice('Save changes: (y/n)')
    if not choice.lower().startswith('y'):
        CLIPrompts.info('Aborting.')
        return
    CLIPrompts.info(f'Exporting to configs/config-{label}.yml')
    with open(Path('configs', f'config-{label}.yml'), 'w') as f:
        yaml.dump(data, f)
    if load_yaml().get('label') == label:
        CLIPrompts.info('Exporting to >> config.yml ')
        with open('config.yml', 'w') as f:
            yaml.dump(data, f)
    CLIPrompts.info('Export complete.')


def interactive_editor_loop(data: dict, commands: list[str], label: str) -> bool:
    cmd = CLIPrompts.custom_choice(CLIPrompts.signature(
    ) + f'[italic red](editor/{label})[/italic red] ')
    end = False
    if not any(cmd.startswith(c) for c in commands):
        CLIPrompts.error('Invalid command, type "help" to see the commands')
        return
    if cmd.startswith('peek'):
        tokens = cmd.split(' ')
        for label, value in data.items():
            if len(tokens) > 1 and tokens[1] != label:
                continue
            inspect(value, title=label, methods=False, all=True)
    elif cmd.startswith('set'):
        interactive_mode_parser(cmd, data)
    elif cmd.startswith('exit'):
        exit_prog(label, data)
        end = True
    elif cmd.startswith('help'):
        CLIPrompts.info('Commands:')
        edit_help('peek', 'shows the current config',
                  'peek | peek <group>', 'peek dev')
        edit_help('set', 'sets a property in the config',
                  'set <group> <property> <value>', 'set redis.host=localhost')
        edit_help('exit', 'saves and exits the editor', 'exit', 'exit')
        edit_help('help', 'shows the help menu', 'help', 'help')
    else:
        CLIPrompts.error('Invalid command, type "help" to see the commands')
    return end


def interactive_mode_parser(
    typed_input: str,
    data: dict
) -> None:
    # worst code ever written, wasn't tryna spend all day on this
    typed_input = typed_input.strip().lower()
    tokens = typed_input.split(' ')
    if not tokens:
        CLIPrompts.error(
            'Invalid syntax, <set <group> <property> <value>, (example: set redis.host=localhost)'
        )
        return
    if len(tokens) != 2:
        CLIPrompts.error(
            'Invalid syntax, <set <group> <property> <value>, (example: set redis.host=localhost)')
        return
    context = tokens[0].split('.')
    if len(context) != 2:
        CLIPrompts.error(
            'Invalid syntax, <set <group> <property> <value>, (example: set redis.host=localhost)')
        return

    config_group, prop_token = context[0], context[1].split('=')
    if len(prop_token) != 2:
        CLIPrompts.error(
            'Invalid syntax, <set <group> <property> <value>, (example: set redis.host=localhost)')
        return
    prop, value = prop_token[0], prop_token[1]
    if not valid_args(config_group, prop, value):
        return
    CLIPrompts.info(f'SET -> {typed_input}={value}')
    data[config_group] = value


def valid_args(prefix: str, attr: str, value: str) -> Optional[str]:
    config_type = config_type_map.get(prefix)
    if not config_type:
        CLIPrompts.error(
            f'Unknown config group "{prefix}", available groups are {", ".join(config_type_map.keys())}')
        return None
    config_data = config_type()
    if not attr in config_data.model_fields:
        CLIPrompts.error(
            f'Unknown attribute "{attr}" for {prefix}, available attributes are {", ".join(config_data.model_fields.keys())}')
        return None

    field = config_data.model_fields[attr]

    try:
        prop_type = field.annotation if field.annotation else str
        prop_type(value)
    except Exception as e:
        CLIPrompts.error(f'Invalid value for {field}: {e}')
        return None

    return value
