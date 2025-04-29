from typing import Annotated

from fastapi import APIRouter, Depends, Query

from common.errors import HTTPNotFound

from app.misc.openapi_extra import APITags, NOT_FOUND_404, ROLE_REQUIRED_DEP_RESPONSE

from app.api.users.dependency import AdminRequired

from .dependency import LogServiceDep
from .schema import (
    EventLogResponse,
    LogSummaryResponse,
    LogQueryParams,
    LogQueryResponse
)

log_router = APIRouter(
    prefix="/logs",
    tags=[APITags.event_logs],
    dependencies=[Depends(AdminRequired)],
    responses=ROLE_REQUIRED_DEP_RESPONSE
)


@log_router.get("/summary/", response_model=LogSummaryResponse)
async def get_summary(log_service: LogServiceDep) -> LogSummaryResponse:
    """returns a summary of recent event logs
    Arguments:
        log_service {LogServiceDep}
    Returns:
        LogSummaryResponse
    """
    previous_log = await log_service.get_summary()
    return previous_log


@log_router.get("/search", response_model=LogQueryResponse, responses=NOT_FOUND_404)
async def search_event_logs(
    query_params: Annotated[LogQueryParams, Query()],
    log_service: LogServiceDep
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
    stmnt = log_service.query_params_to_select(query_params)
    total = await log_service.models.count_by(stmnt)
    if total == 0:
        raise HTTPNotFound("No logs found matching the query parameters.")

    filter_stmnt = query_params.apply_to_query(stmnt)
    results = await log_service.models.db.execute(filter_stmnt)
    serialized = [
        EventLogResponse.to_model(model)
        for model in results.scalars().all()
    ]
    return LogQueryResponse.create(serialized, total)


@log_router.get("/today", response_model=LogQueryResponse, responses=NOT_FOUND_404)
async def logs_from_today(
    query_filter: Annotated[LogQueryParams, Query()],
    log_service: LogServiceDep
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
    today_stmnt = log_service.from_today()

    complete_stmnt = log_service.query_params_to_select(
        query_filter,
        today_stmnt
    )
    total = await log_service.models.count_by(complete_stmnt)
    if total == 0:
        raise HTTPNotFound("No logs found matching the query parameters.")
    filter_stmnt = query_filter.apply_to_query(complete_stmnt)
    results = await log_service.models.db.execute(filter_stmnt)
    serialized = [
        EventLogResponse.to_model(model)
        for model in results.scalars().all()
    ]
    return LogQueryResponse.create(serialized, total)
