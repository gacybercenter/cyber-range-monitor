from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from sqlalchemy.sql.functions import func
from typing import Any
from typing import Optional

from app.common.errors import HTTPNotFound
from app.common.models import QueryFilters
from app.services.utils import CRUDService
from app.models import LogLevel, EventLog
from app.schemas.log_schema import (
    LogMetaData,
    LogLevelTotals,
    LastLogs,
    LogQueryParams
)


class LogService(CRUDService[EventLog]):
    def __init__(self) -> None:
        super().__init__(EventLog)

    async def get_log_meta(self, db: AsyncSession) -> LogMetaData:
        '''
            gets the meta data for the logs to display on a dashboard 
            including the total number of logs for each log level and the
            most recent logs for critical and error levels
        '''
        totals = await self.log_level_totals(db)
        prev_logs = await self.previous_logs(db)
        return LogMetaData(totals=totals, previous_logs=prev_logs)

    async def log_level_totals(self, db: AsyncSession) -> LogLevelTotals:
        '''
        Builds a dictionary using the property names for the 'LogLevelTotals'
        model using the severity levels and returns the total number of logs 
        for each log level.
        Arguments:
            db {AsyncSession} 

        Returns:
            LogLevelTotals 
        '''
        totals = {}
        for levels in LogLevel:
            stmnt = select(func.count(EventLog.id)).where(
                EventLog.log_level == levels.value)
            totals[levels.value.lower()] = self.count_query_total(stmnt, db)
        return LogLevelTotals(**totals)

    async def most_recent_log_by(self, predicate: Any, db: AsyncSession) -> Optional[EventLog]:
        '''
        Returns the most recent log that matches the given predicate.

        Arguments:
            predicate {Any} -- 
            db {AsyncSession} -- 

        Returns:
            Optional[EventLog] -- _description_
        '''

        stmnt = select(EventLog).filter(
            predicate
        ).order_by(
            EventLog.timestamp.desc()
        ).limit(1)
        result = await db.execute(stmnt)
        return result.scalars().first()

    async def previous_logs(self, db: AsyncSession) -> LastLogs:
        '''
        Returns the most recent logs for the critical and error log levels.

        - The property names for LastLogs are 'last_critical' and 'last_error'

        - LogLevel.CRITICAL and LogLevel.ERROR are the log levels to filter by and 
        to lower are 'critical' and 'error' respectively.

        Arguments:
            db {AsyncSession}

        Returns:
            LastLogs -- _description_
        '''
        prev_logs = {}
        for levels in (LogLevel.CRITICAL, LogLevel.ERROR):
            key_name = 'last_' + levels.value.lower()
            item = await self.most_recent_log_by(
                EventLog.log_level == levels.value,
                db
            )
            prev_logs[key_name] = item
        return LastLogs(**prev_logs)

    async def resolve_query_params(
        self,
        query_filter: QueryFilters,
        log_query: LogQueryParams
    ) -> Select:
        query = select(EventLog)

        if log_query.before:
            query = query.where(EventLog.timestamp < log_query.before)

        if log_query.after:
            query = query.where(EventLog.timestamp > log_query.after)

        if log_query.msg_like:
            query = query.where(EventLog.message.ilike(
                f"%{log_query.msg_like}%")
            )

        if log_query.order_by_timestamp:
            query = query.order_by(EventLog.timestamp.desc())

        return query

    async def get_query_meta(self, skip: int, limit: int, query: Select, db: AsyncSession) -> QueryMetaResult:
        total_count = await self.count_query_total(query, db)
        if total_count == 0:
            raise HTTPNotFound("No logs found with the given parameters")

        return QueryMetaResult.init(total_count, skip, limit)
