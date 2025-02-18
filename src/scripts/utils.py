from rich.console import Console





def script_hdr(
    console: Console, 
    script_name: str,
    style: str = 'bold blue'
) -> None:
    console.print(
        '[bold blue] << [/bold blue]'
        '[bold red]~(range_monitor_api)[/bold red]'
        '[italic green]$[/italic green]' 
        f'[{style}]{script_name}[/{style}]'
        '[bold blue] >> [/bold blue]'
    )