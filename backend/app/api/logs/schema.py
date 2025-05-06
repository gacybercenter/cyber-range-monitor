# schema.py
from datetime import UTC, datetime
import logging
from typing import Annotated, Any, Dict, List, Literal, Optional, Self, Union

from pydantic import Field

from app.common.schemas.http import CustomBaseModel, RequestSchema, ResponseSchema
from app.common.types import LogLevels


class LogEntry(CustomBaseModel):
    '''A schema representing the output of a log entry in the websocket'''
    timestamp: Annotated[datetime, Field(
        ...,
        description="Time when the log was created"
    )]

    level: Annotated[LogLevels, Field(
        ...,
        description="Severity level of the log"
    )]

    logger_name: Annotated[str, Field(
        ...,
        description="Name of the logger that created the log"
    )]

    message: Annotated[str, Field(
        ...,
        description="The log message content"
    )]

    exception_info: Annotated[Optional[str], Field(
        default=None,
        description="Exception traceback if any"
    )]

    module: Annotated[str, Field(
        ...,
        description="Module where the log was created"
    )]

    extra: Annotated[Optional[Dict[str, Any]], Field(
        default=None,
        description="Additional context data"
    )]

    @classmethod
    def create(cls, record: logging.LogRecord) -> Self:
        '''Creates a LogEntry from a logging.LogRecord object

        Args:
            record: The log record to convert

        Returns:
            LogEntry: The converted log entry
        '''
        exc_info = None
        if record.exc_info:
            fmtr = logging.Formatter()
            exc_info = fmtr.formatException(record.exc_info)

        extra = {
            k: v for k, v in record.__dict__.items()
            if k not in cls.model_fields and not k.startswith("_")
        }

        return cls(
            timestamp=datetime.fromtimestamp(record.created, UTC),
            level=record.levelname,  # type: ignore
            logger_name=record.name,
            message=record.getMessage(),
            exception_info=exc_info,
            extra=extra if extra else None,
            module=record.module
        )


class LogFilter(CustomBaseModel):
    '''Filter criteria for log entries'''
    logger_names: Annotated[set[str] | None, Field(
        default=None,
        description="Filter by logger names"
    )]

    levels: Annotated[set[LogLevels] | None, Field(
        default=None,
        description="Filter by log levels"
    )]

    module: Annotated[str | None, Field(
        default=None,
        description="Filter by module name"
    )]

    message_contains: Annotated[str | None, Field(
        default=None,
        description="Filter by text in message"
    )]

    from_timestamp: Annotated[datetime | None, Field(
        default=None,
        description="Filter logs after this time"
    )]

    to_timestamp: Annotated[datetime | None, Field(
        default=None,
        description="Filter logs before this time"
    )]

    def is_unset(self) -> bool:
        '''Check if all filter criteria are unset

        Returns:
            bool: True if all criteria are None
        '''
        return all(v is None for v in self.model_dump().values())

    def matches(self, record: LogEntry) -> bool:
        '''Checks if the log record matches the filter criteria.

        Args:
            record: The record to check

        Returns:
            bool: Whether the record matches the filter
        '''
        if self.logger_names and record.logger_name not in self.logger_names:
            return False

        if self.levels and record.level not in self.levels:
            return False

        if self.module and record.module != self.module:
            return False

        if self.message_contains and self.message_contains.lower() not in record.message.lower():
            return False

        if self.from_timestamp and record.timestamp < self.from_timestamp:
            return False

        if self.to_timestamp and record.timestamp > self.to_timestamp:
            return False

        return True


LogCommand = Literal['filter', 'pause', 'resume']


class CommandResponse(ResponseSchema):
    success: Annotated[bool, Field(
        ...,
        description="Success of the command execution"
    )]
    status: Annotated[str, Field(
        ...,
        description="Status of the command execution"
    )]

    @classmethod
    def fail(cls, status: str) -> dict:
        '''Sets the command response to failed.

        Args:
            status (str): The status of the command

        Returns:
            CommandResponse: The updated command response
        '''
        res = cls(
            success=False,
            status=status
        )
        return res.model_dump()

    @classmethod
    def ok(cls, status: str) -> dict:
        '''Sets the command response to success.

        Args:
            status (str): The status of the command

        Returns:
            CommandResponse: The updated command response
        '''
        res = cls(
            success=True,
            status=status
        )
        return res.model_dump()        


class WebSocketCommand(RequestSchema):
    '''The types of commands that can be sent to the websocket'''
    command: Annotated[LogCommand, Field(
        ...,
        description="Command to execute on the websocket connection"
    )]

    filter: Annotated[Optional[LogFilter], Field(
        default=None,
        description="Filter to apply to the logs"
    )]

    def is_filter(self) -> bool:
        '''Checks if the command is a filter command.

        Returns:
            bool: Whether it is a filter command
        '''
        return self.command == 'filter' and self.filter is not None

    def is_pause(self) -> bool:
        '''Checks if the command is a pause command.

        Returns:
            bool: Whether it is a pause command
        '''
        return self.command == 'pause'

    def is_resume(self) -> bool:
        '''Checks if the command is a resume command.

        Returns:
            bool: Whether it is a resume command
        '''
        return self.command == 'resume'


# Base response schema for WebSocket
class WebSocketResponseBase(ResponseSchema):
    '''Base class for WebSocket responses'''
    type: Annotated[str, Field(
        ...,
        description="Type of the response"
    )]

    timestamp: Annotated[datetime, Field(
        default_factory=lambda: datetime.now(UTC),
        description="Time when the response was created"
    )]


class LogEntryResponse(WebSocketResponseBase):
    '''Response containing a log entry'''
    type: Annotated[Literal["log"], Field(
        default="log",
        description="Type of the response"
    )]

    data: Annotated[LogEntry, Field(
        ...,
        description="The log entry"
    )]


class SocketInfo(WebSocketResponseBase):
    '''Response containing an informational message'''
    type: Annotated[Literal["info"], Field(
        default="info",
        description="Type of the response"
    )]

    message: Annotated[str, Field(
        ...,
        description="The informational message"
    )]


class ErrorResponse(WebSocketResponseBase):
    '''Response containing an error message'''
    type: Annotated[Literal["error"], Field(
        default="error",
        description="Type of the response"
    )]

    message: Annotated[str, Field(
        ...,
        description="The error message"
    )]


class PingResponse(WebSocketResponseBase):
    '''Response for a ping message'''
    type: Annotated[Literal["ping"], Field(
        default="ping",
        description="Type of the response"
    )]
