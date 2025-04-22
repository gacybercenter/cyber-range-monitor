from sqlalchemy.ext.asyncio import AsyncSession

from app import config

from app.db.models import EventLogLevel, EventLog

from rich.console import Console


log_config = config.get_config_yml().logging
LEVEL_STYLES = {
    EventLogLevel.INFO: "bold green",
    EventLogLevel.WARNING: "bold yellow",
    EventLogLevel.ERROR: "bold red",
    EventLogLevel.CRITICAL: "bold magenta",
}
console = Console()

def print_log(log: EventLog) -> None:
    """prints an event log to the stdout

    Arguments:
        log {EventLog}
    """

    level_color = LEVEL_STYLES.get(log.log_level, "bold white")
    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    format_msg = (
        f"[grey][[/grey]"
        f"[blue]{timestamp}[/blue]"
        f"[grey] | [/grey]"
        f"[{level_color}]{log.log_level}[/{level_color}]"
        f"[grey]][/grey] - "
        f"[white]{log.message}[/white]"
    )
    console.print(format_msg)


async def create_event_log(
    level: EventLogLevel,
    message: str,
    db: AsyncSession
) -> EventLog | None:
    """creates a new event log in the database

    Arguments:
        level {EventLogLevel} -- the event log level
        message {str} -- the event log message
        db {AsyncSession} -- the database session
    Returns:
        Optional[EventLog] -- the created event log
    """
    if EventLogLevel(log_config.event_log_level) < level:
        return None
    new_log = EventLog(log_level=str(level), message=message)
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log


async def info(log_msg: str, db: AsyncSession) -> None:
    """Creates a "info" level EventLog

    Arguments:
        log_msg {str}
        db {AsyncSession}
    Returns:
        None
    """
    await create_event_log(EventLogLevel.INFO, log_msg, db)


async def warning(log_msg: str, db: AsyncSession) -> None:
    """Creates a "warning" level EventLog if the MIN_LOG_LEVEL allows

    Arguments:
        log_msg {str}
        db {AsyncSession}
    """
    await create_event_log(EventLogLevel.WARNING, log_msg, db)


async def error(log_msg: str, db: AsyncSession, label: str) -> None:
    """Creates an "error" level EventLog if the MIN_LOG_LEVEL allows

    Arguments:
        log_msg {str} -- the log message
        db {AsyncSession} -- the database session
        label {str} -- the error label of the log message
    """
    log_msg = f"{label} >> {log_msg}"
    await create_event_log(EventLogLevel.ERROR, log_msg, db)


async def critical(log_msg: str, db: AsyncSession) -> None:
    """Creates a "critical" level EventLog"""
    await create_event_log(EventLogLevel.CRITICAL, log_msg, db)
