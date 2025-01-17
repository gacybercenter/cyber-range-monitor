from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from api.models.logs import LogLevel
from typing import Optional, List


class ReadLog(BaseModel):
    log_level: LogLevel
    message: str
    timestamp: datetime

    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True
    )


class LogQueryParams(BaseModel):
    before: Optional[datetime] = None
    after: Optional[datetime] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    msg_like: Optional[str] = None


class QueryFilterData(BaseModel):
    log_data: List[ReadLog]
    current_page: int


class TodayLogsResponse(BaseModel):
    log_data: list[ReadLog]
    current_page: int
    date: datetime
    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True
    )
    
class RealtimeLogResponse(BaseModel):
    log_data: list[ReadLog]
    next_timestamp: datetime
    model_config = ConfigDict(
        from_attributes=True
    )