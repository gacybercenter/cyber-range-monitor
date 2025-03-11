from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from .levels import EventLogLevel
from app.core.schemas import (
    APIQueryRequest,
    APIQueryResponse,
    CustomBaseModel
)


class CreateLogBody(CustomBaseModel):
    """request body for creating a new event log"""

    log_level: Annotated[EventLogLevel, Field(
        ...,
        description="The log level of the log to create"
    )]
    message: Annotated[str, Field(..., description="The message of the log")]


class EventLogRead(CustomBaseModel):
    """represents a event log returned from the API"""

    log_level: EventLogLevel
    message: str
    timestamp: datetime


class LogQueryParams(APIQueryRequest):
    """the query params for searching through the logs"""

    order_by_timestamp: Annotated[bool | None, Field(
        True, 
        description="To filter the output by timestamp"
    )]
    log_level: Annotated[EventLogLevel | None, Field(
        None,
        description="To filter the output by log level"
    )]
    msg_like: Annotated[str | None, Field(
        None, 
        description="To filter the output by message"
    )]


class EventLogLevelTotals(CustomBaseModel):
    """represents the total number of logs for each log level"""
    info: int
    warning: int
    error: int
    critical: int


class LastLogs(CustomBaseModel):
    """represents the most recent logs for the critical and error log levels"""
    last_critical: EventLogRead | None
    last_error: EventLogRead | None


class LogQueryResponse(APIQueryResponse[EventLogRead]):
    """the logs returned from a query"""

    @classmethod
    def create(
        cls,
        query_total: int,
        db_out: list[Any],
        params: LogQueryParams,
    ) -> "LogQueryResponse":
        '''Creates a LogQueryResponse object from the query results
        Arguments:
            query_total {int} -- the total number of items returned from the statement, excluding the limit
            db_out {list[Any]} -- the query results into serialized models
            params {LogQueryParams} -- the query params used to get the results
        Returns:
            LogQueryResponse -- the response object
        '''
        items = [EventLogRead.to_model(item) for item in db_out]
        return LogQueryResponse.from_results(
            db_out=items,
            query_total=query_total,
            query_params=params
        )
        


class LogMetaData(CustomBaseModel):
    """the event log meta data to display in a dashboard"""
    totals: Annotated[EventLogLevelTotals, Field(
        ...,
        description="The total count of each log level"
    )]
    previous_logs: Annotated[LastLogs, Field(
        ..., description="The last error and critical log metadata"
    )]
