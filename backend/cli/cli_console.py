from typing import Any

from rich.console import Console


_console = Console()


def clear() -> None:
    _console.clear()


def print_stdout(msg: Any) -> None:
    _console.print(msg)


def signature() -> str:
    return (
        '[italic green]~[/italic green] '
        '([italic blue]range_monitor_api[/italic blue])'
        '[italic green]$[/italic green]'
    )


def info(msg: str) -> None:
    print_stdout(f'[italic blue] ** INFO ** [/italic blue] | {msg}')


def header(style: str, script_name: str) -> None:
    print_stdout(
        '[bold blue] << [/bold blue]'
        f'{signature()}'
        f'[{style}]{script_name}[/{style}]'
        '[bold blue] >> [/bold blue]'
    )


def warn(msg: str) -> None:
    print_stdout(f'[italic yellow]** WARNING ** [/italic yellow] | {msg}')


def error(msg: str) -> None:
    print_stdout(f'[italic red]** ERROR ** | [/italic red] {msg}')


def read(leader: str = '') -> str:
    choice = _console.input(signature() + leader)
    return f'{leader}{choice}'.strip()


def choice(prompt: str, leader: str = '') -> str:
    print_stdout(
        f'[bold green] ? [/bold green] [italic white] {prompt} [/italic white] [bold green] ? [/bold green]'
    )
    return read(leader)


def custom_choice(msg: str) -> str:
    return _console.input(msg)
