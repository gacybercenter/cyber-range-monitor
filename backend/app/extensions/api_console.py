from datetime import datetime

from rich.console import Console

from app import config

app_config = config.get_config_yml().app

_console = Console(color_system='auto')

def get_console() -> Console:
    return _console

def prints(msg: str) -> None:
    '''prints a message to the stdout if console is enabled

    Arguments:
        msg {str} -- the msg to print
    '''
    if not app_config.console_enabled:
        return
    _console.print(msg)


def clears() -> None:
    '''clears the stdout'''
    _console.clear()


def debug(msg: str) -> None:
    if not app_config.debug:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fmt_msg = (
        "[grey][[/grey]"
        f"[blue]{now}[/blue]"
        "[grey] | [/grey]"
        "[bold gray]DEBUG[/bold gray]"
        "[grey]][/grey] - "
        f"[white]{msg}[/white]"
    )
    prints(fmt_msg)

