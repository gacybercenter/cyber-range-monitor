from pydantic import Field
from typing import Dict, Any, Optional, List, Literal, Annotated
from datetime import datetime
import uuid

from app.common.types import LevelNames

from app.common.schemas.http import CustomBaseModel

CommandType = Literal["PAUSE", "RESUME", "UPDATE_FILTER"]


class LogEntry(CustomBaseModel):
    id: Annotated[str, Field(
        ...,
        description="Unique identifier for the log entry"
    )]
    timestamp: Annotated[datetime, Field(
        ...,
        description="When the log was created"
    )]
    level: Annotated[
        LevelNames, Field(..., description="Log severity level")
    ]
    logger_name: Annotated[str, Field(
        ...,
        description="Name of the logger that created this record"
    )]
    message: Annotated[str, Field(..., description="Log message content")]
    function: Annotated[str, Field(
        ...,
        description="Function that generated the log"
    )]
    file_path: Annotated[str, Field(
        ...,
        description="Path to the file that generated the log"
    )]
    line_number: Annotated[int, Field(
        ..., 
        description="Line number in the file"
    )]
    process_id: Annotated[int, Field(..., description="Process ID")]
    thread_id: Annotated[int, Field(..., description="Thread ID")]
    exception: Annotated[Optional[str], Field(
        default=None, 
        description="Exception details if any"
    )]
    extra: Annotated[dict[str, Any], Field(
        default=None,
        description="Additional context data"
    )]

    @classmethod
    def create(cls, record: Dict[str, Any]) -> "LogEntry":
        """Create a LogEntry from a loguru record"""
        return cls(
            id=str(uuid.uuid4()),
            timestamp=record["time"],
            level=record["level"].name,
            logger_name=record["name"],
            message=record["message"],
            function=record["function"],
            file_path=record["file"].path,
            line_number=record["line"],
            process_id=record["process"].id,
            thread_id=record["thread"].id,
            exception=record["exception"],
            extra=record["extra"]
        )

    


class LogFilter(CustomBaseModel):
    """Filter criteria for logs"""
    min_level: Annotated[LevelNames | None, Field(
        default=None, 
        description="Minimum log level to include"
    )]
    logger_names: Annotated[list[str] | None, Field(
        default=None, 
        description="List of logger names to include"
    )]
    message_contains: Annotated[str | None, Field(
        default=None,
        description="Filter logs containing this text"
    )]
    exclude_message_contains: Annotated[Optional[str], Field(
        default=None,
        description="Filter out logs containing this text"
    )]

    def matches_entry(self, log_entry: LogEntry) -> bool:
        levels = ["TRACE", "DEBUG", "INFO",
                  "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

        if self.min_level and levels.index(log_entry.level) < levels.index(self.min_level):
            return False

        if self.logger_names and log_entry.logger_name not in self.logger_names:
            return False

        if self.message_contains and self.message_contains not in log_entry.message:
            return False

        if self.exclude_message_contains and self.exclude_message_contains in log_entry.message:
            return False

        return True


class LogSocketCommand(CustomBaseModel):
    """Command sent from client to server to control log streaming"""
    type: Annotated[CommandType, Field(
        ...,
        description="Command type"
    )]
    data: Annotated[dict[str, Any], Field(
        default=None,
        description="Command data"
    )]
