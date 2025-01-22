from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from datetime import datetime, timezone
from sqlalchemy.sql.functions import func
from typing import Optional

from api.models import LogLevel, EventLog
from api.db.crud import CRUDService
from api.main.schemas.logs import LogQueryParams
from api.utils.generics import QueryMetaResult
from api.utils.errors import ResourceNotFound
from api.utils.generics import QueryMetaResult


class LogService(CRUDService[EventLog]):
    def __init__(self) -> None:
        super().__init__(EventLog)

    def logs_from_today(self) -> Select:
        return select(EventLog).where(
            func.date(EventLog.timestamp) == func.current_date()
        ).order_by(
            EventLog.timestamp.desc()
        )

    async def resolve_query_params(self, log_query: LogQueryParams) -> Select:
        query = select(EventLog)

        if log_query.before:
            query = query.where(EventLog.timestamp < log_query.before)

        if log_query.after:
            query = query.where(EventLog.timestamp > log_query.after)

        if log_query.msg_like:
            query = query.where(EventLog.message.ilike(
                f"%{log_query.msg_like}%")
            )

        if log_query.log_levels:
            query = query.where(EventLog.log_level.in_(log_query.log_levels))

        if log_query.order_by_timestamp:
            query = query.order_by(EventLog.timestamp.desc())

        return query

    async def get_query_meta(self, skip: int, limit: int, query: Select, db: AsyncSession) -> QueryMetaResult:
        total_count = await self.count_query_total(query, db)
        if total_count == 0:
            raise ResourceNotFound("No logs found with the given parameters")

        return QueryMetaResult.init(total_count, skip, limit)

    async def real_time_query(
        self,
        current_timestamp: datetime,
        log_level: Optional[LogLevel],
    ) -> Select:
        current_timestamp = datetime.now(timezone.utc)

        query = select(EventLog).where(
            EventLog.timestamp >= current_timestamp
        )

        if log_level:
            query = query.where(EventLog.log_level == log_level)

        return query.order_by(EventLog.timestamp.asc())
