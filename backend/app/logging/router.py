from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.errors import HTTPNotFound

from app.extensions.openapi_extra import APITags

from app.users.dependency import AdminRequired

from .dependency import LogServiceDep
from .schema import (
    LogMetaData, 
    LogQueryParams, 
    LogQueryResponse
)

log_router = APIRouter(
    prefix="/logs", 
    tags=[APITags.event_logs], 
    dependencies=[Depends(AdminRequired)]
)


@log_router.get("/summary/", response_model=LogMetaData)
async def summary(log_service: LogServiceDep) -> LogMetaData:
    """returns a summary of recent event logs
    Arguments:
        log_service {LogServiceDep}
    Returns:
        LogMetaData
    """
    previous_log = await log_service.get_log_meta()
    return previous_log


@log_router.get("/search/", response_model=LogQueryResponse)
async def search(
    query_params: Annotated[LogQueryParams, Query()], log_service: LogServiceDep
) -> LogQueryResponse:
    """Searches the logs based on the query parameters
    Arguments:
        query_params {Annotated[LogQueryParams, Query} -- the query params
        log_service {LogServiceDep} -- the log service dep
    Raises:
        HTTPNotFound: if no logs are found matching the query parameters
    Returns:
        LogQueryResponse -- the logs that match the query parameters
    """
    stmnt = await log_service.resolve_query_params(None, query_params)
    total = await log_service.count_total(stmnt)
    if total == 0:
        raise HTTPNotFound("No logs found matching the query parameters.")
    filter_stmnt = query_params.apply_to_query(stmnt)
    results = await log_service.execute(filter_stmnt)

    return LogQueryResponse.create(total, results, query_params)


@log_router.get("/today/", response_model=LogQueryResponse)
async def logs_from_today(
    query_filter: Annotated[LogQueryParams, Query()], log_service: LogServiceDep
) -> LogQueryResponse:
    """Given a query filter, returns the logs from today that match the filter

    Arguments:
        query_filter {Annotated[LogQueryParams, Query} the query params
        log_service {LogServiceDep} -- the log service dep

    Raises:
        HTTPNotFound: if no logs are found matching the query parameters

    Returns:
        LogQueryResponse -- the logs that match the query parameters
    """
    today_stmnt = await log_service.logs_from_today()

    complete_stmnt = await log_service.resolve_query_params(today_stmnt, query_filter)
    total = await log_service.count_total(complete_stmnt)
    if total == 0:
        raise HTTPNotFound("No logs found matching the query parameters.")
    filter_stmnt = query_filter.apply_to_query(complete_stmnt)
    results = await log_service.execute(filter_stmnt)

    return LogQueryResponse.create(total, results, query_filter)
