from inspect import signature
from typing import Any
from rich.console import Console
from rich import prompt


class CLIPrompts:
    _console = Console()

    @staticmethod
    def clear() -> None:
        CLIPrompts._console.clear()

    @staticmethod
    def print(msg: Any) -> None:
        CLIPrompts._console.print(msg)

    @staticmethod
    def signature() -> str:
        return ' [italic green]~[/italic green]([italic blue]range_monitor_api[/italic blue])[italic green]$[/italic green] '

    @staticmethod
    def info(msg: str) -> None:
        CLIPrompts.print(
            f'[italic blue] ** INFO ** [/italic blue]'
            f'| {msg}'
        )

    @staticmethod
    def header(style: str, script_name: str) -> None:
        CLIPrompts.print(
            '[bold blue] << [/bold blue]'
            f'{CLIPrompts.signature()}'
            f'[{style}]{script_name}[/{style}]'
            '[bold blue] >> [/bold blue]'
        )

    @staticmethod
    def warn(msg: str) -> None:
        CLIPrompts.print(
            f'[italic yellow]** WARNING ** [/italic yellow] | {msg}'
            f'{msg}'
        )

    @staticmethod
    def error(msg: str) -> None:
        CLIPrompts.print(
            f'[italic red]** ERROR ** | [/italic red] {msg}'
        )

    @staticmethod
    def read(leader: str = '') -> str:
        choice = CLIPrompts._console.input(
            CLIPrompts.signature() + leader
        )
        return f'{leader}{choice}'.strip()

    @staticmethod
    def choice(prompt: str, leader: str = '') -> str:
        CLIPrompts.print(
            f'[bold green] ? [/bold green] [italic white] {prompt} [/italic white] [bold green] ? [/bold green]'
        )
        return CLIPrompts.read(leader)

    @staticmethod
    def custom_choice(msg: str) -> str:
        return CLIPrompts._console.input(msg)
