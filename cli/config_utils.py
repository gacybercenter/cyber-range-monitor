import os
from rich.table import Table
from rich import box

from app.config import running_config, Settings
from scripts.prompts import CLIPrompts


class ConfigUtils:
    @staticmethod
    def show_help() -> None:
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

        CLIPrompts.print(table)

    @staticmethod
    def show_env() -> None:
        app_env = os.getenv('APP_ENV', 'not-set')
        env_file = f'.{app_env}.env'
        with open(env_file, 'r') as f:
            CLIPrompts.print(
                f'[bold blue]APP_ENV=[/bold blue]{app_env} - [italic green]file={env_file}[/italic green]'
            )
            CLIPrompts.print(
                f'[italic green]{f.read()}[/italic green]'
            )

    @staticmethod
    def create_template() -> tuple:
        Settings.load()
        base = running_config()
        required_fields = set()
        for k in base.model_fields.keys():
            if base.model_fields[k].is_required() and not base.model_fields[k].default:
                required_fields.add(k)

        return (base.model_dump(), required_fields)

    @staticmethod
    def verbose_config() -> None:
        Settings.load()
        config = running_config()
        CLIPrompts.print(
            config.model_dump_json(indent=4)
        )
