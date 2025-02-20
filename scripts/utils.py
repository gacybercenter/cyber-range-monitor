import os
from typing import Optional
import toml
from rich.console import Console

from app.common import console



def pyproject_reader(app_root: str, key: Optional[str] = None) -> dict:
    '''Loads content of pyproject.toml file given a path to the app rot 
    and returns the content or a the metadata of a given key

    Arguments:
        path {str} -- _path to pyproject.toml file

    Keyword Arguments:
        key {Optional[str]} -- _key to metadata (default: {None})

    Returns:
        dict -- the content of the pyproject.toml file or the metadata of a given key
    '''
    
    base = toml.load(os.path.join(app_root, 'pyproject.toml'))
    if not key:
        return base
    return base[key]


def script_hdr(
    script_name: str,
    style: str = 'bold blue'
) -> None:
    '''Script header for CLI scripts

    Arguments:
        console {Console} --
        script_name {str} -- 

    Keyword Arguments:
        style {str} -- _description_ (default: {'bold blue'})
    '''
    console = Console()
    console.print(
        '[bold blue] << [/bold blue]'
        '[bold red]~(range_monitor_api)[/bold red]'
        '[italic green]$[/italic green]' 
        f'[{style}]{script_name}[/{style}]'
        '[bold blue] >> [/bold blue]'
    )