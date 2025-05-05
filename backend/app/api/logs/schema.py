

from datetime import UTC, datetime
import logging
from typing import Annotated, Any, Dict, List, Literal, Self

from pydantic import Field
from app.common.types import LogLevels

from app.common.schemas.http import CustomBaseModel, RequestSchema, ResponseSchema


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

    module: Annotated[str, Field(
        ...,
        description="Module where the log was created"
    )]

    function: Annotated[str | None, Field(
        default=None,
        description="Function that created the log"
    )]

    line_number: Annotated[int | None, Field(
        default=None,
        description="Line number in the source code"
    )]

    process_id: Annotated[int | None, Field(
        default=None,
        description="Process ID"
    )]

    thread_id: Annotated[int | None, Field(
        default=None,
        description="Thread ID"
    )]

    thread_name: Annotated[str | None, Field(
        default=None,
        description="Thread name"
    )]
    exception_info: Annotated[str | None, Field(
        default=None,
        description="Exception traceback if any"
    )]

    extra: Annotated[Dict[str, Any] | None, Field(
        default=None,
        description="Additional context data"
    )]

    @classmethod
    def create(cls, record: logging.LogRecord) -> Self:
        '''creates a LogEntry from a logging.LogRecord object
        Returns:
            Self: _the log entry object_
        '''
        exc_info = None
        if record.exc_info:
            fmtr = logging.Formatter()
            exc_info = fmtr.formatException(record.exc_info)

        extra = {
            k: v for k, v in record.__dict__.items()
            if not k in LogEntry.model_fields and not k.startswith("_")
        }

        return cls(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,  # type: ignore
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            process_id=record.process,
            thread_id=record.thread,
            thread_name=record.threadName,
            exception_info=exc_info,
            extra=extra if extra else None
        )


class LogFilter(CustomBaseModel):
    logger_names: Annotated[List[str] | None, Field(
        default=None,
        description="Filter by logger names"
    )]

    levels: Annotated[List[LogLevels] | None, Field(
        default=None,
        description="Filter by log levels"
    )]

    module: Annotated[str | None, Field(
        default=None,
        description="Filter by module name"
    )]

    function: Annotated[str | None, Field(
        default=None,
        description="Filter by function name"
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
        dumped = self.serialize()
        return not dumped

    def matches(self, record: LogEntry) -> bool:
        '''Checks if the log record matches the filter criteria.

        Args:
            record (LogEntry): _the record to check_

        Returns:
            bool: _whether it matches_
        '''
        if self.logger_names and record.logger_name not in self.logger_names:
            return False

        if self.levels and record.level not in self.levels:
            return False

        if self.module and record.module != self.module:
            return False

        if self.function and record.function != self.function:
            return False

        if self.message_contains and self.message_contains.lower() not in record.message.lower():
            return False

        if self.from_timestamp and record.timestamp < self.from_timestamp:
            return False

        if self.to_timestamp and record.timestamp > self.to_timestamp:
            return False

        return True


LogCommands = Literal['filter', 'pause', 'resume']


class WebsocketCommand(RequestSchema):
    '''The types of commands that can be sent to the websocket'''
    command: Annotated[LogCommands, Field(
        ...,
        description="Command to execute on the websocket connection"
    )]
    filter: Annotated[LogFilter | None, Field(
        default=None,
        description="Filter to apply to the logs"
    )]

    
    def is_filter(self) -> bool:
        '''Checks if the command is a filter command.

        Returns:
            bool: _whether it is a filter command_
        '''
        return self.command == 'filter' and self.filter is not None 
    
    def is_pause(self) -> bool:
        '''Checks if the command is a pause command.

        Returns:
            bool: _whether it is a pause command_
        '''
        return self.command == 'pause'
    
    def is_resume(self) -> bool:
        '''Checks if the command is a resume command.

        Returns:
            bool: _whether it is a resume command_
        '''
        return self.command == 'resume'

SocketMsgType = Literal['notice', 'log', 'error', 'ping']


class WebsocketResponse(ResponseSchema):

    response_type: Annotated[SocketMsgType, Field(
        ...,
        description="Type of the response message"
    )]

    data: Annotated[dict | None, Field(
        default=None,
        description="The data to send in the response"
    )]

    timestamp: Annotated[datetime, Field(
        ...,
        description="Time when the response was created"
    )]

    message: Annotated[str | None, Field(
        default=None,
        description="The message to send in the response"
    )]

    @classmethod
    def as_notice(cls, message: str) -> dict[str, Any]:
        timestamp = datetime.now(UTC)
        return cls(
            response_type='notice',
            timestamp=timestamp,
            message=message,
            data=None
        ).serialize()

    @classmethod
    def as_error(cls, message: str) -> dict[str, Any]:
        timestamp = datetime.now(UTC)
        return cls(
            response_type='error',
            timestamp=timestamp,
            message=message,
            data=None
        ).serialize()

    @classmethod
    def as_log(
        cls,
        *,
        entry: LogEntry,
        message: str | None = None,
    ) -> dict[str, Any]:
        timestamp = datetime.now(UTC)
        response = cls(
            data=entry.serialize(),
            timestamp=timestamp,
            message=message,
            response_type='log'
        )
        return response.serialize()

    @classmethod
    def as_ping(cls) -> dict[str, Any]:
        timestamp = datetime.now(UTC)
        response = cls(
            timestamp=timestamp,
            response_type='ping',
            message=None,
            data=None
        )
        return response.serialize()
