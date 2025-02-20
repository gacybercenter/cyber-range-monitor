from typing import Any
from rich.console import Console


class CLIPrompts:
    _console = Console()
    
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
    def read() -> str:
        return CLIPrompts._console.input(
            CLIPrompts.signature()
        )
    
    @staticmethod
    def choice(prompt: str) -> str:
        CLIPrompts.print(
            f'[bold green] ? [/bold green] [italic white] {prompt} [/italic white] [bold green] ? [/bold green]'
        )
        return CLIPrompts.read()


def main() -> None:
    CLIPrompts.info('hello world')
    CLIPrompts.warn('hello world')
    CLIPrompts.error('uh oh')
    CLIPrompts.header('blue', 'test')
    
    
if __name__ == '__main__':
    main()
    
        