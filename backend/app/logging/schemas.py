from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from app.models.enums import LogLevel
from app.shared.schemas import (
    QueryFilters,
    QueryResponse,
    ResponseMessage,
    dt_serializer,
)


class CreateLogBody(BaseModel):
    """request body for creating a new event log"""

    log_level: Annotated[LogLevel, Field(...)]
    message: Annotated[str, Field(...)]


class EventLogRead(BaseModel):
    """represents a event log"""

    log_level: LogLevel
    message: str
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True, json_encoders={datetime: dt_serializer}
    )


class LogQueryParams(QueryFilters):
    """the query params for searching through the logs"""

    order_by_timestamp: Annotated[
        Optional[bool], Field(True, description="To filter the output by timestamp")
    ]
    log_level: Annotated[
        Optional[LogLevel], Field(None, description="To filter the output by log level")
    ]
    msg_like: Annotated[
        Optional[str], Field(None, description="To filter the output by message")
    ]


class LogQueryResponse(QueryResponse):
    """the response for searching through the logs"""

    result: List[EventLogRead]

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class LogLevelTotals(BaseModel):
    """represents the total number of logs for each log level"""

    info: int
    warning: int
    error: int
    critical: int


class LastLogs(BaseModel):
    """represents the most recent logs for the critical and error log levels"""

    last_critical: Optional[EventLogRead]
    last_error: Optional[EventLogRead]


class LogMetaData(BaseModel):
    """the event log meta data to display in a dashboard"""

    totals: LogLevelTotals = Field(..., description="The total count of each log level")
    previous_logs: LastLogs | ResponseMessage = Field(
        ..., description="The last error and critical log metadata"
    )

    @model_serializer()
    def serialize(self) -> dict:
        prev_logs = self.previous_logs.model_dump(exclude_unset=True)
        if not prev_logs:
            prev_logs = ResponseMessage(message="No logs found", success=False)
        return {"totals": self.totals.model_dump(), "previous_logs": prev_logs}
