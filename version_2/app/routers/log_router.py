from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query


from app.common.dependencies import AdminRequired, DatabaseRequired
from app.common.errors import HTTPNotFound
from app.common.logging import LogWriter
from app.common.models import QueryFilters
from app.schemas.log_schema import (
    LogMetaData,
    LogQueryParams,
    LogQueryResponse,
    EventLogRead
)
from app.services.log_service import LogService


log_router = APIRouter(
    prefix='/logs',
    tags=['Logs'],
    dependencies=[Depends(AdminRequired())]
)

log_service = LogService()


@log_router.post('/', response_model=EventLogRead)
async def create_log(log_data: EventLogRead, db: DatabaseRequired) -> EventLogRead:
    logger = LogWriter('EXTERNAL')
    return await logger.create_log(  # type: ignore
        log_data.log_level,
        log_data.message,
        db
    )


@log_router.get('/summary/', response_model=LogMetaData)
async def get_log_summary(db: DatabaseRequired) -> LogMetaData:
    previous_log = await log_service.get_log_meta(db)
    return previous_log


@log_router.get('/search/')
async def search_logs(
    db: DatabaseRequired,
    query_params: Annotated[LogQueryParams, Query()]
) -> LogQueryResponse:
    stmnt = await log_service.resolve_query_params(None, query_params)
    query_meta = await log_service.get_query_meta(
        query_params,
        stmnt,
        db
    )

    if query_meta.total == 0:
        raise HTTPNotFound('No logs found matching the query parameters.')

    stmnt = query_params.apply_to_stmnt(stmnt)

    result = await db.execute(stmnt)
    data = list(result.scalars().all())

    return LogQueryResponse(
        result=data,
        meta=query_meta
    )


@log_router.get('/today/', response_model=LogQueryResponse)
async def logs_from_today(
    query_filter: Annotated[LogQueryParams, Query()],
    db: DatabaseRequired
) -> LogQueryResponse:
    today_stmnt = await log_service.logs_from_today()

    complete_stmnt = await log_service.resolve_query_params(
        today_stmnt,
        query_filter
    )

    query_meta = await log_service.get_query_meta(
        query_filter,
        complete_stmnt,
        db
    )

    if query_meta.total == 0:
        raise HTTPNotFound('No logs found matching the query parameters.')

    resulting_stmnt = query_filter.apply_to_stmnt(complete_stmnt)
    result = await db.execute(resulting_stmnt)
    logs = list(result.scalars().all())

    return LogQueryResponse(
        meta=query_meta,
        result=logs
    )
