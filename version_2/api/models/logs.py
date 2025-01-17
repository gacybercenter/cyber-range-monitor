from enum import IntEnum, StrEnum
from sqlalchemy import Column, Integer, String, Text, CheckConstraint, DateTime
from sqlalchemy.sql import func
from api.db.main import Base

class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    
class LogSeverity(IntEnum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=True, 
        unique=True
    )
    log_level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            log_level.in_([level.value for level in LogLevel]),
            name="valid_log_type"
        ),
    )

    @property
    def severity(self) -> int:
        try:
            return LogSeverity[self.log_level].value # type: ignore
        except KeyError:
            raise ValueError(f"Invalid log level: {self.log_level}")

    def __str__(self) -> str:
        return f"[ {self.log_level} ] | ({self.timestamp}) ] - {self.message}"

    
    def __repr__(self) -> str:
        return f"EventLog(log_level={self.log_level}, message={self.message}, timestamp={self.timestamp})"
