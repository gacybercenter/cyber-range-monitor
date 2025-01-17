from tkinter import SE
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from datetime import datetime, time, timezone
from sqlalchemy.sql.functions import func
from typing import Sequence, Optional
from zoneinfo import ZoneInfo


from api.models import LogLevel, EventLog
from api.db.crud import CRUDService
from api.main.schemas.logs import LogQueryParams
from api.utils.errors import BadRequest


class LogWriter(CRUDService[EventLog]):

    def __init__(self) -> None:
        super().__init__(EventLog)

    async def _insert_new_log(
        self,
        log_level: LogLevel,
        log_msg: str,
        db: AsyncSession
    ) -> EventLog:
        '''
        Inserts a new log into the database 

        Arguments:
            log_level {LogLevel}
            log_msg {str} 
            db {AsyncSession} 

        Returns:
            EventLog 
        '''
        new_log = EventLog(
            log_level=log_level,
            message=log_msg
        )
        await self.insert_model(new_log, db, refresh=True)
        return new_log

    async def info_log(self, log_msg: str, db: AsyncSession) -> EventLog:
        return await self._insert_new_log(LogLevel.INFO, log_msg, db)

    async def warning_log(self, log_msg: str, db: AsyncSession) -> EventLog:
        return await self._insert_new_log(LogLevel.WARNING, log_msg, db)

    async def error_log(self, log_msg: str, db: AsyncSession) -> EventLog:
        return await self._insert_new_log(LogLevel.ERROR, log_msg, db)

    async def critical_log(self, log_msg: str, db: AsyncSession) -> EventLog:
        return await self._insert_new_log(LogLevel.CRITICAL, log_msg, db)


class LogQueryHandler(LogWriter):
    async def count_filter_total(
        self,
        db: AsyncSession,
        q: LogQueryParams
    ) -> int:
        """
        gets the number of logs matching the specified filter criteria.

        Args:
            db: Database session
            q: Query parameters

        Returns:
            Total count of matching logs
        """
        if not db:
            raise ValueError("Database session cannot be None")

        query = select(func.count(EventLog.id))
        query = self._apply_filters(query, q)

        try:
            result = await db.execute(query)
            count = result.scalar()
            return count if count is not None else 0
        except Exception as e:
            await self.error_log(f"Failed to count total: {e}", db)
            raise BadRequest(f"Failed to count total")

    async def get_filtered_logs(
        self,
        db: AsyncSession,
        q: LogQueryParams,
        skip: int = 0,
        limit: int = 50
    ) -> Sequence[EventLog]:
        """
        Uses the query params to filter and return a list of logs.

        Args:
            db: Database session
            q: Query parameters
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence of filtered EventLog objects
        """
        if skip < 0:
            raise BadRequest("Skip value cannot be negative")

        if limit < 1:
            raise BadRequest("Limit must be greater than 0")

        query = select(self.model)
        query = self._apply_filters(query, q)
        query = query.order_by(self.model.timestamp.desc())
        query = query.offset(skip).limit(limit)

        try:
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.error_log(f"Failed to get query logs, exeception info: {e}", db)
            raise BadRequest(
                f"Can not evaluate the results of an invalid query")

    def _apply_filters(self, query: Select, q: LogQueryParams) -> Select:
        """
        Builds a query based on the query params model.

        Args:
            query: Base select statement
            q: Query parameters

        Returns:
            Modified select statement with filters applied
        """
        if q.start and q.end:
            if q.start > q.end:
                raise BadRequest("Start date cannot be after end date")
            query = query.where(self.model.timestamp.between(q.start, q.end))
        else:
            if q.before:
                query = query.where(self.model.timestamp < q.before)
            if q.after:
                query = query.where(self.model.timestamp > q.after)

        if q.msg_like:
            if len(q.msg_like) < 256:
                query = query.where(
                    self.model.message.ilike(f"%{q.msg_like}%"))
            else:
                raise BadRequest("Search string too long")

        return query

    def today_query(self, timezone) -> LogQueryParams:
        current_date = datetime.now(ZoneInfo(timezone))
        start_of_day = datetime.combine(current_date.date(), time.min)
        end_of_day = datetime.combine(current_date.date(), time.max)

        return LogQueryParams(
            start=start_of_day,
            end=end_of_day
        )

    async def real_time_query(
        self,
        current_timestamp: datetime,
        log_level: Optional[LogLevel],
        limit: int,
        db: AsyncSession
    ) -> Sequence[EventLog]:

        current_timestamp = datetime.now(timezone.utc)

        query = select(EventLog).where(
            EventLog.timestamp > current_timestamp
        )

        if log_level:
            query = query.where(EventLog.log_level == log_level)

        query = query.order_by(EventLog.timestamp.asc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


def get_logger() -> LogWriter:
    return LogWriter()
