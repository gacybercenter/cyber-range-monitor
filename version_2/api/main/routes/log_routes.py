
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from api.main.schemas.logs import RealtimeLogResponse
from api.utils.dependencies import needs_db
from api.utils.security.auth import admin_required
from api.main.schemas import LogQueryParams, LogQueryResponse, RealtimeLogResponse
from api.main.services.log_service import LogService
from api.utils.generics import BaseQueryParam
from datetime import datetime, timezone
from api.models import LogLevel

log_router = APIRouter(
    prefix='/logs',
    dependencies=[Depends(admin_required)],
    tags=['audit']
)

log_service = LogService()


@log_router.get('/', response_model=LogQueryResponse)
async def query_log(
    db: needs_db,
    query_params: LogQueryParams = Depends()
) -> LogQueryResponse:
    """
    Retrieve paginated and filtered log entries.

    Args:
        page_num: Page number (1-based)
        db: Database session
        query_params: Filter parameters for the logs

    Returns:
        QueryFilterData containing logs and pagination info

    Raises:
        HTTPException: For invalid page numbers or when no logs are found
    """

    query_stmnt = await log_service.resolve_query_params(query_params)
    query_meta = await log_service.get_query_meta(
        query_params.limit,
        query_params.skip,
        query_stmnt,
        db
    )
    results = await log_service.run_query(query_stmnt.limit(query_params.limit), db)

    return LogQueryResponse(
        meta=query_meta,
        result=results  # type: ignore
    )


@log_router.get('/logs/today', response_model=LogQueryResponse)
async def read_today_logs(
    db: needs_db,
    params: Optional[BaseQueryParam] = None,
) -> LogQueryResponse:
    """
    Retrieve paginated log entries from today in the specified timezone.

    Args:
        page_num: Page number (1-based)
        db: Database session
        timezone: Timezone name (default: UTC)

    Returns:
        TodayLogsResponse containing today's logs and pagination info

    Raises:
        HTTPException: For invalid page numbers or when no logs are found
    """
    if params is None:
        params = BaseQueryParam()  # type: ignore

    stmnt = log_service.logs_from_today()
    meta = await log_service.get_query_meta(params.skip, params.limit, stmnt, db)
    stmnt = stmnt.limit(params.limit).offset(params.skip)

    results = await log_service.run_query(stmnt, db)
    return LogQueryResponse(
        meta=meta,
        result=results  # type: ignore
    )


@log_router.get('/real-time', response_model=RealtimeLogResponse)
async def real_time_logs(
    db: needs_db,
    last_timestamp: datetime = Query(default=datetime.now(timezone.utc)),
    log_level: Optional[LogLevel] = Query(default=None),
    limit: int = Query(default=50, le=200, gt=10)
) -> RealtimeLogResponse:

    stmnt = await log_service.real_time_query(last_timestamp, log_level)
    result = await log_service.run_query(stmnt.limit(limit), db)
    next_timestamp = result[-1].timestamp

    return RealtimeLogResponse(
        result=result,  # type: ignore
        next_timestamp=next_timestamp  # type: ignore
    )
