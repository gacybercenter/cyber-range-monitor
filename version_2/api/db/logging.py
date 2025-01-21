from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from rich.console import Console
from typing import Optional

from api.models.logs import LogLevel, EventLog
from api.config.settings import app_config

console = Console()

LOG_LEVEL_STYLES = {
    LogLevel.INFO: "bold green",
    LogLevel.WARNING: "bold yellow",
    LogLevel.ERROR: "bold red",
    LogLevel.CRITICAL: "bold magenta",
    "DEBUG": "bold gray",  # < not an enum bc it's not saved in the database
}


def format_console_log(log: EventLog) -> None:
    level_color = LOG_LEVEL_STYLES.get(
        log.log_level, "bold white")  # type: ignore
    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    stdout = (
        f"[grey][[/grey]"
        f"[blue]{timestamp}[/blue]"
        f"[grey] | [/grey]"
        f"[{level_color}]{log.log_level}[/{level_color}]"
        f"[grey]][/grey] - "
        f"[white]{log.message}[/white]"
    )
    console.print(stdout)


class LogWriter:
    '''
    A instance based convience class for logging events, it is instance
    based so it is scoped and easier to categorize logs
    '''

    def __init__(self, category: Optional[str] = '') -> None:
        self.prefix = category

    def _msg_template(self, message: str):
        return f"{self.prefix} | {message}"

    async def _create_new_log(
        self,
        level: LogLevel,
        log_msg: str,
        db: AsyncSession
    ) -> None:
        if not app_config.LOG_EVENTS:
            return

        new_log = EventLog(
            log_level=level,
            message=self._msg_template(log_msg)
        )

        if app_config.CONSOLE_EVENT_LOGS:
            format_console_log(new_log)

        db.add(new_log)
        await db.commit()

    async def info(self, log_msg: str, db: AsyncSession) -> None:
        await self._create_new_log(LogLevel.INFO, log_msg, db)

    async def warning(self, log_msg: str, db: AsyncSession) -> None:
        await self._create_new_log(LogLevel.WARNING, log_msg, db)

    async def error(self, log_msg: str, db: AsyncSession) -> None:
        await self._create_new_log(LogLevel.ERROR, log_msg, db)

    async def critical(self, log_msg: str, db: AsyncSession) -> None:
        await self._create_new_log(LogLevel.CRITICAL, log_msg, db)

    def debug(self, log_msg: str) -> None:
        '''
        displays a debug message in the console 
        if console messages are enabled, keep in mind
        debug logs are not saved to the database due 
        to them being irrelevant in a production environment  
        and exist for development convenience

        Arguments:
            log_msg {str} -- the debug message 
        '''
        if not app_config.CONSOLE_EVENT_LOGS:
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
        console.print(fmt_msg)
