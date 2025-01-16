from api.models import Log, LogLevel, LogType
from pydantic import BaseModel
from datetime import datetime


class BaseLog(BaseModel):
    level: LogLevel
    type: LogType
    message: str


class AppLog(BaseLog):
    type: LogType = LogType.APPLICATION


class SecurityLog(BaseLog):
    type: LogType = LogType.SECURITY


class TracebackLog(BaseLog):
    type: LogType = LogType.TRACEBACK


class LogResponse(BaseModel):
    meta_data: BaseLog
    severity: int
