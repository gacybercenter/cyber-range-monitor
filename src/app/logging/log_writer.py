from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.logging.log_model import EventLog
from app.models.enums import LogLevel
from app.config import running_config
from .console import log


settings = running_config()


class LogWriter:
    '''A instance based convience class for logging events, it is instance
    based so it is scoped and easier to categorize logs
    '''

    def __init__(self, category: Optional[str] = '') -> None:
        self.prefix: Optional[str] = category

    def _msg_template(self, message: str) -> str:
        return f"({self.prefix}) | {message}"

    async def create_log(
        self,
        level: LogLevel,
        log_msg: str,
        db: AsyncSession
    ) -> Optional[EventLog]:
        if not settings.WRITE_LOGS:
            return None

        new_log = EventLog(
            log_level=str(level),
            message=self._msg_template(log_msg)
        )
        db.add(new_log)
        await db.commit()
        # v-the timestamp will be None if session not refreshed
        await db.refresh(new_log)
        log(new_log, settings.CONSOLE_LOG)
        return new_log

    async def info(self, log_msg: str, db: AsyncSession) -> None:
        '''Creates an "INFO" EventLog

        Arguments:
            log_msg {str} 
            db {AsyncSession}
        Returns:
            None
        '''
        await self.create_log(LogLevel.INFO, log_msg, db)

    async def warning(self, log_msg: str, db: AsyncSession) -> None:
        '''Creates a "WARNING" EventLog

        Arguments:
            log_msg {str} 
            db {AsyncSession}
        Returns:
            None
        '''
        await self.create_log(LogLevel.WARNING, log_msg, db)

    async def error(self, log_msg: str, db: AsyncSession, label: str = '') -> None:
        '''Creates an "ERROR" EventLog

        Arguments:
            log_msg {str} 
            db {AsyncSession}
        Returns:
            None
        '''
        log_msg = label + log_msg
        await self.create_log(LogLevel.ERROR, log_msg, db)

    async def critical(self, log_msg: str, db: AsyncSession) -> None:
        '''Creates an "CRITICAL" EventLog

        Arguments:
            log_msg {str} 
            db {AsyncSession}
        Returns:
            None
        '''
        await self.create_log(LogLevel.CRITICAL, log_msg, db)
