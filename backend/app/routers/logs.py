from typing import Annotated
from fastapi import APIRouter, Body, Depends, Query

from app.logging.schemas import (
    CreateLogBody,
    LogMetaData,
    LogQueryParams,
    LogQueryResponse,
    EventLogRead
)
from app.logging.dependency import LogController
from app.shared.errors import HTTPNotFound
from app.users.dependency import AdminProtected


log_router = APIRouter(
    prefix='/logs',
    tags=['Logs'],
    dependencies=[Depends(AdminProtected)]
)


@log_router.get('/summary/', response_model=LogMetaData)
async def get_summary(log_service: LogController) -> LogMetaData:
    '''returns a summary of recent event logs 
    Arguments:
        log_service {LogController}
    Returns:
        LogMetaData
    '''
    previous_log = await log_service.get_log_meta()
    return previous_log


@log_router.get('/search/')
async def search_logs(
    query_params: Annotated[LogQueryParams, Query()],
    log_service: LogController
) -> LogQueryResponse:
    stmnt = await log_service.resolve_query_params(None, query_params)
    query_meta = await log_service.get_query_meta(
        query_params,
        stmnt
    )
    if query_meta.total == 0:
        raise HTTPNotFound('No logs found matching the query parameters.')

    stmnt = query_params.apply_to_stmnt(stmnt)

    result = await log_service.db.execute(stmnt)

    return LogQueryResponse(
        result=list(result.scalars().all()),
        meta=query_meta
    )


@log_router.get('/today/', response_model=LogQueryResponse)
async def logs_from_today(
    query_filter: Annotated[LogQueryParams, Query()],
    log_service: LogController
) -> LogQueryResponse:
    '''Given a query filter, returns the logs from today that match the filter

    Arguments:
        query_filter {Annotated[LogQueryParams, Query} the query params
        log_service {LogController} -- the log service dep

    Raises:
        HTTPNotFound: if no logs are found matching the query parameters

    Returns:
        LogQueryResponse -- the logs that match the query parameters
    '''
    today_stmnt = await log_service.logs_from_today()

    complete_stmnt = await log_service.resolve_query_params(
        today_stmnt,
        query_filter
    )

    query_meta = await log_service.get_query_meta(
        query_filter,
        complete_stmnt
    )

    if query_meta.total == 0:
        raise HTTPNotFound('No logs found matching the query parameters.')

    resulting_stmnt = query_filter.apply_to_stmnt(complete_stmnt)
    result = await log_service.db.execute(resulting_stmnt)
    logs = list(result.scalars().all())

    return LogQueryResponse(
        meta=query_meta,
        result=logs
    )
