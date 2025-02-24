from datetime import datetime
from typing import Any
from rich.console import Console
from app.models.enums import LogLevel

# quality of life stylized messages for the console 
# that are easy to read and color coded

LOG_LEVEL_STYLES = {
    LogLevel.INFO: "bold green",
    LogLevel.WARNING: "bold yellow",
    LogLevel.ERROR: "bold red",
    LogLevel.CRITICAL: "bold magenta"
}



_console = Console()
    
def log(log: Any, console_log: bool) -> None:
    '''Given a EventLog model, formats the log 

    Arguments:
        log {EventLog} -- 
    '''
    if not console_log:
        return
    
    level_color = LOG_LEVEL_STYLES.get(
        log.log_level,  # type: ignore
        "bold white"
    )
    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    format_msg = (
        f"[grey][[/grey]"
        f"[blue]{timestamp}[/blue]"
        f"[grey] | [/grey]"
        f"[{level_color}]{log.log_level}[/{level_color}]"
        f"[grey]][/grey] - "
        f"[white]{log.message}[/white]"
    )
    _console.print(format_msg)

def debug(log_msg: str) -> None:
    '''displays a debug message in the console 
    if console messages are enabled, keep in mind
    debug logs are not saved to the database due 
    to them being irrelevant in a production environment  
    and exist for development convenience

    Arguments:
        log_msg {str} -- the debug message 
    '''
    if not settings.CONSOLE_LOG:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fmt_msg = (
        "[grey][[/grey]"
        f"[blue]{now}[/blue]"
        "[grey] | [/grey]"
        "[bold gray]DEBUG[/bold gray]"
        "[grey]][/grey] - "
        f"[white]{log_msg}[/white]"
    )
    _console.print(fmt_msg)

def print(message: str) -> None:
    '''prints a message to the console

    Arguments:
        message {str} -- the message to print
    '''
    _console.print(message)
    
def clear() -> None:
    '''clears the console'''
    _console.clear()

