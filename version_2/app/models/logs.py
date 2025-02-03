from datetime import datetime
from enum import StrEnum
from sqlalchemy import Integer, String, Text, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from sqlalchemy.sql import func
from app.models.base import Base


class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


SEVERITY_MAP = {
    LogLevel.INFO: 1,
    LogLevel.WARNING: 2,
    LogLevel.ERROR: 3,
    LogLevel.CRITICAL: 4
}


class EventLog(Base):
    __tablename__ = "event_logs"

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True
    )
    log_level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(), 
        nullable=False
    )

    severity = mapped_column(Integer, nullable=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not kwargs.get('severity'):
            self.severity = SEVERITY_MAP.get(LogLevel(self.log_level), -1)

    def __str__(self) -> str:
        return f"[ {self.log_level} ] | ({self.timestamp}) ] - {self.message}"

    def __repr__(self) -> str:
        return f"EventLog(log_level={self.log_level}, message={self.message}, timestamp={self.timestamp})"
