from scripts.utils.environ_io import EnvironIO
from app.core.config.app_config import (
    BuildConfig,
    RedisConfig,
    DatabaseConfig,
    SessionConfig,
    DocumentationConfig,
    BaseAppConfig,
    config_prefixes
)
import cmd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import print as rprint

console = Console()


class ShellUtils:
    @staticmethod
    def try_resolve_key() -> None:
        pass


class ConfigBuilder(cmd.Cmd):
    intro =
    prompt = '[bold blue](~config)$[/bold blue] '

    def __init__(self, section: str, config_data: dict, parent_shell) -> None:
        super().__init__()
        self.section = section
        self.config_data = config_data
        self.parent_shell = parent_shell
        self.prompt = f'[bold blue](~config/[italic red]{
            self.section}[/italic red]])$[/bold blue] '
        self.intro = Panel.fit(
            f"[bold green]App Builder (~config\\{self.section})[/bold green]\n"
            "Type [bold]help[/bold] or [bold]?[/bold] to list commands.",
            title="Configuration CLI",
            border_style="blue"
        )
        self.config_class = config_prefixes[section]

    def do_set(self, arg):
        try:
            key_abrv, *value_parts = arg.split()
            value = ' '.join(value_parts)
