from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from app.core.interfaces import DatabaseService

from app.db.models import EventLog, EventLogLevel
from .schema import (
    LastLogs,
    EventLogLevelTotals,
    LogMetaData,
    LogQueryParams
)


class LogService(DatabaseService[EventLog]):
    """the controller for the event logs"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(EventLog, db)

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
        self, log_level: EventLogLevel, limit: int | None
    ) -> list[EventLog]:
        """Returns all of the logs for the given log level

        Arguments:
            log_level {EventLogLevel} --the log level to filter by
            limit {Optional[int]} -- the limit of entries to return 

        Returns:
            list[EventLog] -- the logs for the given log level
        """
        stmnt = (
            select(EventLog)
            .where(EventLog.log_level == log_level)
            .order_by(EventLog.timestamp.desc())
        )
        if limit:
            stmnt = stmnt.limit(limit)

        result = await self.models.execute_on_all(stmnt)
        return result

    async def level_totals(self) -> EventLogLevelTotals:
        """
        Builds a dictionary using the property names for the 'EventLogLevelTotals'
        model using the severity levels and returns the total number of logs
        for each log level.

        Returns:
            EventLogLevelTotals
        """
        totals = {}
        for levels in EventLogLevel:
            stmnt = select(
                func.count(EventLog.id)
            ).where(EventLog.log_level == levels)
            totals[levels.value.lower()] = await self.models.count_rows_by(stmnt)

        return EventLogLevelTotals(**totals)

    async def most_recent_logs(self, predicate: Any) -> EventLog | None:
        """Returns the most recent log that matches the given predicate.

        Arguments:
            predicate {Any} -- the additional condition to filter the logs by

        Returns:
            Optional[EventLog] -- _description_
        """

        stmnt = (
            select(EventLog)
            .filter(predicate)
            .order_by(EventLog.timestamp.desc())
            .limit(1)
        )
        result = await self.models.execute(stmnt)
        return result

    async def previous_logs(self) -> LastLogs:
        """Returns the most recent logs for the critical and error log levels.

        - The property names for LastLogs are 'last_critical' and 'last_error'

        - EventLogLevel.CRITICAL and EventLogLevel.ERROR are the log levels to filter by and
        to lower are 'critical' and 'error' respectively.
        Returns:
            LastLogs
        """
        prev_logs = {}
        for levels in (EventLogLevel.CRITICAL, EventLogLevel.ERROR):
            key_name = "last_" + levels.value.lower()
            item = await self.most_recent_logs(EventLog.log_level == levels.value)
            prev_logs[key_name] = item
        return LastLogs(**prev_logs)

    def query_params_to_stmnt(
        self,
        log_query: LogQueryParams,
        base_stmnt: Select | None = None
    ) -> Select:
        """resolves the query params into an SQL query (
        excluding the "QueryFilter" props which are applied later
        )

        Arguments:
            base_stmnt {Optional[Select]} -- an optional base statement to apply the query filters to
            log_query {LogQueryParams} -- _description_

        Returns:
            Select -- a statement with the resolved query params
        """

        if base_stmnt is None:
            base_stmnt = select(EventLog)

        if log_query.log_level:
            base_stmnt = base_stmnt.where(
                EventLog.log_level == log_query.log_level
            )
        if log_query.msg_like:
            base_stmnt = base_stmnt.where(
                EventLog.message.ilike(f"%{log_query.msg_like}%")
            )
        if log_query.order_by_timestamp:
            base_stmnt = base_stmnt.order_by(EventLog.timestamp.desc())

        return base_stmnt

    def logs_from_today(self) -> Select:
        '''filters the event logs for only logs that 
        were created today

        Returns:
            Select -- the select statement
        '''
        return select(EventLog).where(
            EventLog.timestamp >= func.current_date()
        )

