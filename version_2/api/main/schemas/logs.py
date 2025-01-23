from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

from api.models.logs import LogLevel
from api.utils.generics import BaseQueryParam, QueryResponse


class EventLogRead(BaseModel):
    log_level: LogLevel
    message: str
    timestamp: datetime

    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True
    )


class LogQueryParams(BaseQueryParam):
    order_by_timestamp: Optional[bool] = True
    before: Optional[datetime] = None
    after: Optional[datetime] = None
    msg_like: Optional[str] = None
    log_levels: Optional[List[LogLevel]] = None

    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True
    )


class LogQueryResponse(QueryResponse):
    result: List[EventLogRead]

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class RealtimeLogResponse(BaseModel):
    result: List[EventLogRead]
    next_timestamp: datetime
