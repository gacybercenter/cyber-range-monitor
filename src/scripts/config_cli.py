import os
from typing import Any, Callable, Optional
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from app.config.main import running_config, AppSettings


def config_help(console: Console) -> None:
    table = Table(
        title='# Build Settings Docs #',
        header_style='bold white',
        border_style='bright_blue',
        box=box.DOUBLE_EDGE
    )
    config = running_config()

    table.add_column('Property Name', style='cyan', no_wrap=True)
    table.add_column('Property Type', style='magenta')
    table.add_column('Default', style='yellow')
    table.add_column('Summary', style='green')
    table.add_column('Required', style='red')

    for name, field in config.model_fields.items():
        table.add_row(
            name,
            type(getattr(config, name)).__name__,
            str(field.default),
            field.description or 'Not provided',
            'Yes' if field.is_required() else 'No'
        )

    console.print(table)


def config_as_env() -> None:
    AppSettings.load_config()

    console = Console()
    config = running_config()
    for name in config.model_fields:
        console.print(
            f'[bold blue]{name}[/bold blue]=[bold green]{getattr(config, name)}[/bold green]'
        )


def config_as_json() -> None:
    AppSettings.load_config()
    console = Console()
    config = running_config()
    console.print(
        config.model_dump_json(indent=4)
    )


def create_config_template() -> tuple:
    AppSettings.load_config()
    base = running_config()
    required_fields = set()
    for k in base.model_fields.keys():
        if base.model_fields[k].is_required() and not base.model_fields[k].default:
            required_fields.add(k)

    return (base.model_dump(), required_fields)


class Command(BaseModel):
    help: str
    action: Callable[['CreateConfig', Optional[str]], Any]


def preview(config: 'CreateConfig', complete_cmd: Optional[str]) -> None:
    fields_like = complete_cmd.split(' ', 1)[1] if len(  # type: ignore
        complete_cmd.split(' ', 1)) > 1 else None  # type: ignore

    table = Table(
        title="Configuration Preview",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="blue",
        padding=(0, 2)
    )

    table.add_column("Setting", style="cyan", justify="right")
    table.add_column("Value", style="green")

    for key, v in config.template.items():
        if not fields_like or (fields_like and key.lower().startswith(fields_like)):
            table.add_row(key, str(v))
    panel = Panel(
        table,
        title="[bold white]Configuration Settings[/bold white]",
        border_style="bright_blue",
        padding=(1, 2)
    )

    config.console.print(panel)


def show_docs(config: 'CreateConfig', _) -> None:
    config_help(config.console)


def disable_docs(config: 'CreateConfig', _) -> None:
    keys = [key
        for key in config.template.keys() if key.lower().startswith('doc')
    ]

    for doc_setting in keys:
        config.set_field(f'{doc_setting}=None')


def try_build(config: 'CreateConfig', _) -> bool:
    if not len(config.required) == 0:
        config.console.print(
            '[red]Configuration is not ready to build missing required fields[/red]'
            f'[italic white]{", ".join(config.required)}[/italic white]'
        )

        return False

    try:
        AppSettings.test_config(config.template)
        config.console.print('[green]Build successful[/green]')
        return True
    except Exception as e:
        config.console.print(
            f'[red]BuildError:[/red]\n[italic white]Details:\n\t{e}[/italic white]'
        )
        return False


def export(config: 'CreateConfig', complete_cmd: Optional[str]) -> None:
    if not try_build(config, None):
        config.console.print(
            '[bold red]Error: [/bold red] cannot export an invalid configuration'
        )

    app_env = complete_cmd.split(' ', 1)[1] if len(
        complete_cmd.split(' ', 1)) > 1 else None  

    if not app_env:
        app_env = os.environ.get('APP_ENV', 'dev')
        
    env_file_name = f'.{app_env}.env'

    exist_ok = f'The {env_file_name} already exists. Do you want to overwrite it? (TYPE "YES"): '
    if os.path.exists(env_file_name) and input(exist_ok).lower().strip() != 'yes':
        config.console.print(
            '[bold red]Aborting export[/bold red]'
        )
        return

    with open(env_file_name, 'w') as f:
        for key, value in config.template.items():
            f.write(f'{key}={value}\n')

    config.console.print(
        f'[green]Exported configuration to {env_file_name}[/green]'
    )


def exit_app(_, __) -> None:
    exit(0)


def show_help(config: 'CreateConfig', _) -> None:
    config.console.print('[italic white]Commands[/italic white]')
    for cmd, cmd_model in config.cmd_map.items():
        config.console.print(
            f'\t[bold blue]{cmd}[/bold blue] - {cmd_model.help}'
        )


class CreateConfig:
    def __init__(self) -> None:
        template, required = create_config_template()
        self.template: dict = template
        self.required: set = required
        self.console = Console()
        self.cmd_map = {
            'no-docs': Command(
                help='Disables the documentation routes',
                action=disable_docs
            ),
            'try-build': Command(
                help='Tests to see if the configuration is ready to build',
                action=try_build
            ),
            'preview': Command(
                help='previews the current configuration, optional prefix to filter configurations (preview <prefix>)',
                action=preview
            ),
            'export': Command(
                help='exports the configuration to a .env file (export [optional_file_name | default=".env"])',
                action=export
            ),
            'exit': Command(
                help='exits the application',
                action=exit_app
            ),
            'show-docs': Command(
                help='displays the documentation for app settings',
                action=show_docs
            ),
            'help': Command(
                help='Displays the commands for the CLI',
                action=show_help
            ),
            'clear': Command(
                help='Clears the screen of the CLI',
                action=lambda _, __: os.system(
                    'cls' if os.name == 'nt' else 'clear'
                )
            )
        }

    def set_field(self, input_str: str) -> None:
        tokenized = input_str.split('=')
        if len(tokenized) != 2:
            self.console.print('[red]Invalid input[/red]')
            return

        field_name, value = tokenized
        field_name = field_name.strip().upper()
        if not field_name in self.template:
            self.console.print(
                f'[red]Unknown property "{field_name}" type help to view properties[/red]'
            )
            return

        self.template[field_name] = tokenized[1]
        self.console.print(
            f'[bold green]Set {field_name}[/bold green] to {value}'
        )

        if field_name in self.required:
            self.required.remove(field_name)

    def show_self(self, fields_like: Optional[str]) -> None:

        self.console.print(
            '[italic white]Set configuration[/italic white]'
        )
        for key, v in self.template.items():
            if not fields_like or (fields_like and key.lower().startswith(fields_like)):
                self.console.print(
                    f'\t[bold blue]{key}[/bold blue]\t\t[bold green]{v}[/bold green]'
                )

    def show_prefix(self, prefix: str) -> None:
        for key, v in self.template.items():
            if key.lower().startswith(prefix):
                self.console.print(
                    f'\t[bold blue]{key}[/bold blue]\t\t[bold green]{v}[/bold green]'
                )

    def show_cmds(self) -> None:
        for cmd, cmd_model in self.cmd_map.items():
            self.console.print(
                f'[bold blue]{cmd}[/bold blue] - {cmd_model.__doc__}'
            )

    def app_loop(self) -> None:
        if not os.environ.get('APP_ENV'):
            os.environ['APP_ENV'] = 'dev'
        self.console.clear()
        self.console.print(
            '[italic white]## Welcome to the config builder, type "help" for a list of commands ##[/italic white]')
        self.console.print(
            '[italic blue] ~ To set a field in the build settings for the API type [bold red]PROP_NAME=VALUE[/bold red] ~ [/italic blue]'
        )
        self.console.print(
            f'[italic white] ~ Config Template from APP_ENV={os.environ.get("APP_ENV")} ~[/italic white]'
        )

        while True:
            choice = self.console.input(
                '[bold blue]~config(api)#[/bold blue] '
            ).strip()
            lowered_choice = choice.lower()
            try:
                tokens = lowered_choice.split()
                if len(tokens) > 0 and tokens[0] in self.cmd_map:
                    self.cmd_map[tokens[0]].action(self, choice)
                else:
                    self.set_field(choice)
            except Exception as e:
                self.console.print(f'[red]Bad input: {e}[/red]')
