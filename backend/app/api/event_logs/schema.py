from datetime import datetime
from typing import Annotated

from pydantic import Field

from common.schemas.http import (
    RequestSchema,
    QueryParameters,
    PagedResponse,
    CustomBaseModel,
    ResponseSchema
)

from .levels import EventLogLevel


class CreateLogBody(RequestSchema):
    """request body for creating a new event log"""

    log_level: Annotated[EventLogLevel, Field(
        ...,
        description="The log level of the log to create"
    )]
    message: Annotated[str, Field(..., description="The message of the log")]


class EventLogResponse(ResponseSchema):
    """represents a event log returned from the API"""
    log_level: EventLogLevel
    message: str
    timestamp: datetime


class LogQueryParams(QueryParameters):
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
    last_critical: EventLogResponse | None
    last_error: EventLogResponse | None


class LogQueryResponse(PagedResponse[EventLogResponse]):
    """the logs returned from a query"""
    data: Annotated[list[EventLogResponse], Field(
        ...,
        description="The logs returned from the query"
    )]


class LogSummaryResponse(CustomBaseModel):
    """the event log meta data to display in a dashboard"""
    totals: Annotated[EventLogLevelTotals, Field(
        ...,
        description="The total count of each log level"
    )]
    previous_logs: Annotated[LastLogs, Field(
        ..., description="The last error and critical log metadata"
    )]
