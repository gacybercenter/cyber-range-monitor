from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query


from app.common.dependencies import AdminRequired, requires_db
from app.common.errors import HTTPNotFound
from app.common.logging import LogWriter
from app.common.models import QueryFilters
from app.models.enums import LogLevel
from app.models.logs import EventLog
from app.schemas.log_schema import (
    LogMetaData,
    LogQueryParams,
    LogQueryResponse,
    EventLogRead
)
from app.services.controllers.log_service import LogService


log_router = APIRouter(
    prefix='/logs',
    tags=['Logs', 'Auditing', 'Admin Only'],
    dependencies=[Depends(AdminRequired())]
)

log_service = LogService()


@log_router.post('/', response_model=EventLogRead)
async def create_log(log_data: EventLogRead, db: requires_db) -> EventLogRead:
    logger = LogWriter('EXTERNAL')
    return await logger.create_log(  # type: ignore
        log_data.log_level,
        log_data.message,
        db
    )


@log_router.get('/summary', response_model=LogMetaData)
async def get_log_summary(db: requires_db) -> LogMetaData:
    previous_log = await log_service.get_log_meta(db)
    return previous_log
     
@log_router.get('/search')
async def search_logs(
    db: requires_db,
    query_params: Annotated[LogQueryParams, Query()],
    query_filter: Annotated[QueryFilters, Query()],
) -> LogQueryResponse:
    stmnt = await log_service.resolve_query_params(
        query_params
    )
    query_meta = await log_service.get_query_meta(
        query_filter,
        stmnt,
        db
    )
    
    if query_meta.total == 0:
        raise HTTPNotFound('No logs found matching the query parameters.')

    stmnt = query_filter.apply_to_stmnt(stmnt)
    
    result = await db.execute(stmnt)
    data = list(result.scalars().all())
    
    return LogQueryResponse(
        result=data,
        meta=query_meta
    )

@log_router.get('/today', response_model=List[LogLevel])
async def logs_from_today(
    query_filter: Annotated[QueryFilters, Query()],
    db: requires_db
) -> List[LogLevel]:
    result = await log_service.occured_today(query_filter, db)
    return result # type: ignore
    










    
    
    
    
    
    
    
    
    
    
    
    
     
     
     
     
     
     
     
     
     
     
    
    
    
    
    
    





