from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from rich.console import Console


from typing import Optional
from app.models.enums import LogLevel
from app.models.logs import EventLog
from app import settings


config = settings.get_config_yml().api_config
level_styles = {
    LogLevel.INFO: "bold green",
    LogLevel.WARNING: "bold yellow",
    LogLevel.ERROR: "bold red",
    LogLevel.CRITICAL: "bold magenta",
}
_console = Console()


def prints(msg: str) -> None:
    if not config.console_enabled:
        return
    _console.print(msg)


def clears() -> None:
    _console.clear()


def debug(msg: str) -> None:
    if not config.debug:
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


def print_log(log: EventLog) -> None:
    '''prints an event log if ENABLE_CONSOLE is True

    Arguments:
        log {EventLog}
    '''
    if not config.console_enabled:
        return

    level_color = level_styles.get(log.log_level, "bold white")
    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    format_msg = (
        f"[grey][[/grey]"
        f"[blue]{timestamp}[/blue]"
        f"[grey] | [/grey]"
        f"[{level_color}]{log.log_level}[/{level_color}]"
        f"[grey]][/grey] - "
        f"[white]{log.message}[/white]"
    )
    prints(format_msg)


async def init_log(
    level: LogLevel,
    message: str,
    db: AsyncSession
) -> Optional[EventLog]:
    '''creates a new event log in the database

    Arguments:
        level {LogLevel} -- the event log level
        message {str} -- the event log message
        db {AsyncSession} -- the database session
    Returns:
        Optional[EventLog] -- the created event log
    '''
    if LogLevel(config.min_log_level) < level:
        return None
    new_log = EventLog(
        log_level=str(level),
        message=message
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log


async def info(log_msg: str, db: AsyncSession) -> None:
    '''Creates a "info" level EventLog if MIN_LOG_LEVEL is set to "INFO"

    Arguments:
        log_msg {str} 
        db {AsyncSession}
    Returns:
        None
    '''
    await init_log(LogLevel.INFO, log_msg, db)


async def warning(log_msg: str, db: AsyncSession) -> None:
    '''Creates a "warning" level EventLog if the MIN_LOG_LEVEL allows

    Arguments:
        log_msg {str} -- _description_
        db {AsyncSession} -- _description_
    '''
    await init_log(LogLevel.WARNING, log_msg, db)


async def error(log_msg: str, db: AsyncSession, label: str) -> None:
    '''Creates an "error" level EventLog if the MIN_LOG_LEVEL allows

    Arguments:
        log_msg {str} -- the log message
        db {AsyncSession} -- the database session
        label {str} -- the error label of the log message
    '''
    log_msg = f'{label} >> {log_msg}'
    await init_log(LogLevel.ERROR, log_msg, db)


async def critical(log_msg: str, db: AsyncSession) -> None:
    '''Creates a "critical" level EventLog'''
    await init_log(LogLevel.CRITICAL, log_msg, db)
