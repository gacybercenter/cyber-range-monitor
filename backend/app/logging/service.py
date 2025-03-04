from typing import Any, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from app.models.enums import LogLevel
from app.models.logs import EventLog
from app.shared.crud_mixin import CRUDService
from app.shared.errors import HTTPNotFound
from app.shared.schemas import QueryFilters, QueryResultData

from .schemas import LastLogs, LogLevelTotals, LogMetaData, LogQueryParams


class LogService(CRUDService[EventLog]):
    """the controller for the event logs"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(EventLog)
        self.db = db

    async def get_log_meta(self) -> LogMetaData:
        """gets the meta data for the logs to display on a dashboard
        including the total number of logs for each log level and the
        most recent logs for critical and error levels

        Arguments:
            db: AsyncSession
        Returns:
            LogMetaData
        """
        totals = await self.level_totals()
        prev_logs = await self.previous_logs()
        return LogMetaData(totals=totals, previous_logs=prev_logs)

    async def get_by_level(
        self, log_level: LogLevel, limit: Optional[int]
    ) -> list[EventLog]:
        """Returns all of the logs for the given log level

        Arguments:
            db {AsyncSession} --
            log_level {LogLevel} --
            limit {Optional[int]} --

        Returns:
            list[EventLog] -- _description_
        """
        stmnt = (
            select(EventLog)
            .where(EventLog.log_level == log_level)
            .order_by(EventLog.timestamp.desc())
        )
        if limit:
            stmnt = stmnt.limit(limit)

        result = await self.db.execute(stmnt)
        return list(result.scalars().all())

    async def level_totals(self) -> LogLevelTotals:
        """
        Builds a dictionary using the property names for the 'LogLevelTotals'
        model using the severity levels and returns the total number of logs
        for each log level.
        Arguments:
            db {AsyncSession}

        Returns:
            LogLevelTotals
        """
        totals = {}
        for levels in LogLevel:
            stmnt = select(func.count(EventLog.id)).where(EventLog.log_level == levels)
            totals[levels.value.lower()] = await self.count_query_total(stmnt, self.db)

        return LogLevelTotals(**totals)

    async def most_recent_logs(self, predicate: Any) -> Optional[EventLog]:
        """Returns the most recent log that matches the given predicate.

        Arguments:
            predicate {Any} --
            db {AsyncSession} --

        Returns:
            Optional[EventLog] -- _description_
        """

        stmnt = (
            select(EventLog).filter(predicate).order_by(EventLog.timestamp.desc()).limit(1)
        )
        result = await self.db.execute(stmnt)
        return result.scalars().first()

    async def previous_logs(self) -> LastLogs:
        """Returns the most recent logs for the critical and error log levels.

        - The property names for LastLogs are 'last_critical' and 'last_error'

        - LogLevel.CRITICAL and LogLevel.ERROR are the log levels to filter by and
        to lower are 'critical' and 'error' respectively.

        Arguments:
            db {AsyncSession}

        Returns:
            LastLogs
        """
        prev_logs = {}
        for levels in (LogLevel.CRITICAL, LogLevel.ERROR):
            key_name = "last_" + levels.value.lower()
            item = await self.most_recent_logs(EventLog.log_level == levels.value)
            prev_logs[key_name] = item
        return LastLogs(**prev_logs)

    async def resolve_query_params(
        self, base_stmnt: Optional[Select], log_query: LogQueryParams
    ) -> Select:
        """resolves the query params into an SQL query (excluding the "QueryFilter" props which are applied later)

        Arguments:
            base_stmnt {Optional[Select]} -- an optional base statement to apply the query filters to
            log_query {LogQueryParams} -- _description_

        Returns:
            Select -- a statement with the resolved query params
        """

        if base_stmnt is None:
            base_stmnt = select(EventLog)

        if log_query.log_level:
            base_stmnt = base_stmnt.where(EventLog.log_level == log_query.log_level)
        if log_query.msg_like:
            base_stmnt = base_stmnt.where(
                EventLog.message.ilike(f"%{log_query.msg_like}%")
            )
        if log_query.order_by_timestamp:
            base_stmnt = base_stmnt.order_by(EventLog.timestamp.desc())

        return base_stmnt

    async def get_query_meta(
        self, query_filter: QueryFilters, query: Select
    ) -> QueryResultData:
        total_count = await self.count_query_total(query, self.db)
        if total_count == 0:
            raise HTTPNotFound("No logs found with the given parameters")

        return QueryResultData.init(
            total_count,
            query_filter.skip,  # type: ignore
            query_filter.limit,  # type: ignore
        )

    async def logs_from_today(self) -> Select:
        return select(EventLog).where(EventLog.timestamp >= func.current_date())
