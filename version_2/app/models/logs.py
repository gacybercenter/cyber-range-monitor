from datetime import datetime
from sqlalchemy import Integer, String, Text, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func
from app.models.base import Base
from .enums import LogLevel

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
    message: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    def __str__(self) -> str:
        return f"[ {self.log_level} ] | ({self.timestamp}) ] - {self.message}"

    def __repr__(self) -> str:
        return f"EventLog(log_level={self.log_level}, message={self.message}, timestamp={self.timestamp})"
