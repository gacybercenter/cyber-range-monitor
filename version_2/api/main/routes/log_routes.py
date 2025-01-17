
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api.main.schemas.logs import RealtimeLogResponse
from api.utils.dependencies import needs_db
from api.utils.security.auth import admin_required
from api.main.schemas import QueryFilterData, LogQueryParams, TodayLogsResponse
from api.main.services.log_service import LogQueryHandler
from api.utils.errors import ResourceNotFound, BadRequest
from datetime import datetime, timezone
from api.models import LogLevel


log_router = APIRouter(
    prefix='/audit',
    dependencies=[Depends(admin_required)],
    tags=['audit']
)

log_query_handler = LogQueryHandler()
RESULTS_PER_PAGE = 50


@log_router.get('/logs/{page_num}', response_model=QueryFilterData)
async def read_logs(
    page_num: int,
    db: needs_db,
    query_params: LogQueryParams = Depends()
) -> QueryFilterData:
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
    if page_num < 1:
        raise BadRequest('Page number must be greater than 0')

    query_total = await log_query_handler.count_filter_total(db, query_params)

    if not query_total:
        raise ResourceNotFound(
            'No logs were found matching the query criteria'
        )

    total_pages = (query_total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    if page_num > total_pages:
        page_num = 1

    skip = (page_num - 1) * RESULTS_PER_PAGE

    log_data = await log_query_handler.get_filtered_logs(
        db,
        query_params,
        skip,
        RESULTS_PER_PAGE
    )

    return QueryFilterData(
        log_data=log_data,  # type: ignore
        current_page=page_num,
    )


@log_router.get('/logs/today/{page_num}', response_model=TodayLogsResponse)
async def read_today_logs(
    page_num: int,
    db: needs_db,
    timezone: str = "UTC"
) -> TodayLogsResponse:
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
    if page_num < 1:
        raise BadRequest("Page number must be greater than 0")

    today_params = log_query_handler.today_query(timezone)
    query_total = await log_query_handler.count_filter_total(db, today_params)

    if not query_total:
        raise ResourceNotFound('No logs found for today, please try again')

    total_pages = (query_total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    if page_num > total_pages:
        page_num = total_pages

    skip = (page_num - 1) * RESULTS_PER_PAGE

    log_data = await log_query_handler.get_filtered_logs(
        db,
        today_params,
        skip,
        RESULTS_PER_PAGE
    )

    return TodayLogsResponse(
        log_data=log_data,  # type: ignore
        current_page=page_num
    )


@log_router.get('/logs/real-time', response_model=TodayLogsResponse)
async def real_time_logs(
    db: needs_db,
    last_timestamp: datetime = Query(default=datetime.now(timezone.utc)),
    log_level: Optional[LogLevel] = Query(default=None),
    limit: int = Query(default=50, le=200, gt=10)
) -> RealtimeLogResponse:

    results = await log_query_handler.real_time_query(
        last_timestamp,
        log_level,
        limit,
        db
    )

    next_timestamp = last_timestamp
    if results:
        next_timestamp = max(log.timestamp for log in results)  # type: ignore

    return RealtimeLogResponse(
        log_data=results,  # type: ignore
        next_timestamp=next_timestamp
    )
