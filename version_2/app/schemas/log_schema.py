from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from typing import Optional, List
from starlette.middleware.sessions import SessionMiddleware
from app.models.enums import LogLevel
from app.common.models import QueryResponse




class CreateLogBody(BaseModel):
    log_level: LogLevel
    message: str

class EventLogRead(BaseModel):
    log_level: LogLevel
    message: str
    timestamp: datetime
    severity: Optional[int]

    model_config = ConfigDict(
        from_attributes=True
    )


class LogQueryParams(BaseModel):
    order_by_timestamp: Optional[bool] = Field(
        True, 
        description="To filter the output by timestamp"
    )
    before: Optional[datetime] = Field(
        None, 
        description="To filter the output by timestamp"
    )
    after: Optional[datetime] = Field(
        None,
        description="To filter the output by timestamp"
    )
    
    msg_like: Optional[str] = Field(
        None, 
        description="To filter the output by message"
    )
    
    severity: int = Field(
        default=0, 
        description="To filter the output by log level"
    )

    model_config = ConfigDict(
        extra='forbid'  
    )
    
    


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
    totals: LogLevelTotals = Field(..., description="The total count of each log level")
    previous_logs: LastLogs = Field(..., description="The last error and critical log metadata")
    
    
    
    
    