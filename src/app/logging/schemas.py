from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Annotated, Optional, List
from app.models.enums import LogLevel
from app.common.models import QueryFilters, QueryResponse, StrictModel, dt_serializer


class CreateLogBody(BaseModel):
    log_level: LogLevel
    message: str


class EventLogRead(BaseModel):
    log_level: LogLevel
    message: str
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: dt_serializer
        }
    )


class LogQueryParams(QueryFilters):
    order_by_timestamp: Annotated[
        Optional[bool],
        Field(
            True,
            description="To filter the output by timestamp"
        )
    ]
    log_level: Annotated[
        Optional[LogLevel],
        Field(
            None,
            description="To filter the output by log level"
        )
    ]
    msg_like: Annotated[
        Optional[str],
        Field(None,  description="To filter the output by message")
    ]

    model_config = ConfigDict(extra='forbid')


class LogQueryResponse(QueryResponse):
    result: List[EventLogRead]

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class LogLevelTotals(BaseModel):
    info: int
    warning: int
    error: int
    critical: int


class LastLogs(BaseModel):
    last_critical: Optional[EventLogRead]
    last_error: Optional[EventLogRead]


class LogMetaData(BaseModel):
    totals: LogLevelTotals = Field(...,
                                   description="The total count of each log level")
    previous_logs: LastLogs = Field(...,
                                    description="The last error and critical log metadata")
