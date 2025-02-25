from typing import Optional
from pydantic_settings import BaseSettings
import typer
from rich.table import Table

from app.configs.main import config_init

from .prompts import CLIPrompts

config_app = typer.Typer()

# the imports are weird to avoid importing modules with initialized
# settings, some of which require a .env file to load from and will
# raise an error if the file is not found, this allows the cli to be
# used to setup the developer environment easily


def config_docs() -> None:
    from app.configs import CONFIG_MAP

    table = Table(
        title='# Build Settings Docs #',
        header_style='bold white',
        border_style='bright_blue'
    )

    table.add_column(
        'Env Prefix',
        style='bright_blue'
    )
    table.add_column('Property Name', style='cyan', no_wrap=True)
    table.add_column('Property Type', style='magenta')
    table.add_column('Default', style='yellow')
    table.add_column('Summary', style='green')
    table.add_column('Required', style='red')

    for config in CONFIG_MAP.keys():
        current = CONFIG_MAP[config]
        current_model = current['config']
        env_prefix = current.get('env_prefix', 'N/A')

        for row_contents in docs_of(current_model, env_prefix):
            table.add_row(*row_contents)


def docs_of(config_type: BaseSettings, env_prefix):
    for name, field in config_type.model_fields.items():
        yield [
            env_prefix,
            name,
            type(getattr(config_type, name)).__name__,
            str(field.default),
            field.description,
            'Yes' if field.is_required() else 'No'
        ]


def show_docs_for(config_prefix: str) -> None:
    import app.configs as CONFIG_MAP
    config = CONFIG_MAP.CONFIG_MAP.get(config_prefix)
    if not config:
        CLIPrompts.error(f'Config: {config_prefix} not found.')
        raise typer.Abort()
    table = Table(
        title=f'{config_prefix} Config Docs',
        header_style='bold white',
        border_style='bright_blue'
    )

    for row in docs_of(config['config'], config['env_prefix']):
        table.add_row(*row)

    CLIPrompts.print(table)


@config_app.command(help='Shows the documentation for the build settings')
def docs() -> None:
    config_docs()


@config_app.command(help='Shows the documentation for a specific config')
def show_docs(prefix: str = typer.Argument(..., help='the config prefix to show')) -> None:
    show_docs_for(prefix)


@config_app.command(help='creates the default environments')
def setup() -> None:
    from scripts.create_env import main
    main()


@config_app.command(help='creates the default settings')
def builder() -> None:
    CLIPrompts.info('Creating .env file template...')
    CLIPrompts.warn(
        'If there is an existing .env file, it will be overwritten. '
    )
    env_name = CLIPrompts.choice(
        'Enter a name for the ENVIRONMENT variable (your file will be saved as <name>.env)')
    CLIPrompts.info(
        f'Creating .env file for {env_name}, please input any of the required values below to proceed')
    from scripts.create_env import create_secrets
    data = create_secrets(env_name)
    from app.configs import CONFIG_MAP
    CLIPrompts.clear()
    CLIPrompts.header('bold green', 'api_config_builder')
    CLIPrompts.print(
        '[bold red] ## [/bold red] ( Type "help" for a list of commands ) [bold red]##[/bold red]'
    )
    while True:
        cmd_input = CLIPrompts.read()
        if cmd_input.lower().startswith('exit'):
            CLIPrompts.info('Exiting...')
            break
        interactive_mode_parser(cmd_input, CONFIG_MAP, data)


def interactive_mode_parser(
    typed_input: str,
    config_map: dict,
    data: dict
) -> None:
    # worst code ever written, wasn't tryna spend all day on this
    typed_input = typed_input.strip()
    lowered = typed_input.lower()
    if lowered.startswith('set'):
        vals = do_set(typed_input, config_map)
        if not vals:
            return
        key, value = vals
        data[key] = value
        CLIPrompts.info(f'SET -> {key}={value}')
    elif lowered == 'docs':
        tokens = typed_input.split(' ')
        if len(tokens) == 1:
            config_docs()
        else:
            show_docs_for(tokens[1])
    elif lowered.startswith('help'):
        CLIPrompts.print(
            '[blue] Commands: [/blue]\n'
            'set <config> <field> <value> - sets a field value\n'
            'docs - shows the documentation for a config or docs <config_name> to show docs for a config\n'
            'preview - shows the current values of the config\n (preview <prefix> to filter by prefix)\n'
            'export - exports the current values to a .env file\n'
        )
    elif lowered.startswith('preview'):
        tokens = typed_input.split(' ')
        if len(tokens) == 1:
            for key, value in data.items():
                CLIPrompts.print(f'{key}={value}')
        else:
            printed = False
            for key, value in data.items():
                if key.startswith(tokens[1]):
                    CLIPrompts.print(f'{key}={value}')
                    printed = True
            if not printed:
                CLIPrompts.warn(
                    f'No values found for the given prefix {tokens[1]}')
    elif lowered.startswith('export'):
        env_name = CLIPrompts.choice('Enter the ENVIRONMENT for the config')
        file = f'{env_name}.env'
        data['ENVIRONMENT'] = env_name
        with open(file, 'w') as f:
            for key, value in data.items():
                f.write(f'{key}={value}\n')
        CLIPrompts.info(f'Config exported to {file}')
        CLIPrompts.warn(
            'Some of the values may be invalid at run time due to type differences, update the env file accordingly')
    elif lowered.startswith('exit'):
        return
    else:
        CLIPrompts.error('Unknown command, type help for a list of commands')


def do_set(typed_input: str, config_map: dict) -> Optional[tuple]:
    parts = typed_input.split(' ')

    if not parts:
        return None
    if len(parts) < 4:
        return None

    prefix, field, value = parts[1], parts[2].upper(), parts[3]
    config_data = config_map.get(prefix)
    if not config_data:
        CLIPrompts.error('Config not found.')
        return None

    target_config = config_data['config']
    target_attr = target_config.model_fields.get(field)
    if not target_attr:
        CLIPrompts.error(f'Unknown field {target_attr} for {prefix}.')
        return None
    env_prefix = config_data.get('env_prefix', None)
    return (env_prefix + target_attr, value)
