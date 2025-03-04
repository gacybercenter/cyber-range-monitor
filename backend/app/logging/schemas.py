from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from app.models.enums import LogLevel
from app.schemas.base import APIQueryRequest, APIQueryResponse, CustomBaseModel


class CreateLogBody(CustomBaseModel):
    """request body for creating a new event log"""

    log_level: Annotated[LogLevel, Field(...)]
    message: Annotated[str, Field(...)]


class EventLogRead(CustomBaseModel):
    """represents a event log"""

    log_level: LogLevel
    message: str
    timestamp: datetime


class LogQueryParams(APIQueryRequest):
    """the query params for searching through the logs"""

    order_by_timestamp: Annotated[
        bool | None, Field(True, description="To filter the output by timestamp")
    ]
    log_level: Annotated[
        LogLevel | None, Field(None, description="To filter the output by log level")
    ]
    msg_like: Annotated[
        str | None, Field(None, description="To filter the output by message")
    ]


class LogLevelTotals(BaseModel):
    """represents the total number of logs for each log level"""

    info: int
    warning: int
    error: int
    critical: int


class LastLogs(BaseModel):
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
        items = [EventLogRead.to_model(item) for item in db_out]
        return LogQueryResponse.from_results(
            db_out=items,
            query_total=query_total,
            query_params=params,
        )


class LogMetaData(BaseModel):
    """the event log meta data to display in a dashboard"""

    totals: LogLevelTotals = Field(..., description="The total count of each log level")
    previous_logs: LastLogs = Field(
        ..., description="The last error and critical log metadata"
    )
