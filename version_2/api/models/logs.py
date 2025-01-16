
from enum import IntEnum, StrEnum
from sqlalchemy import Column, Integer, String, Text, CheckConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict
from sqlalchemy.sql import func

Base = declarative_base()


class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(StrEnum):
    APPLICATION = "APPLICATION"
    SECURITY = "SECURITY"
    TRACEBACK = "TRACEBACK"


SEVERITY_MAP: dict[StrEnum, int] = {
    LogType.APPLICATION: 5,
    LogType.SECURITY: 10,
    LogType.TRACEBACK: 20,
    LogLevel.INFO: 5,
    LogLevel.WARNING: 10,
    LogLevel.ERROR: 20,
    LogLevel.CRITICAL: 30,
}


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            level.in_([level.value for level in LogLevel]),
            name='valid_log_level'
        ),
        CheckConstraint(
            type.in_([log_type.value for log_type in LogType]),
            name='valid_log_type'
        ),
    )

    @property
    def severity(self) -> int:
        return SEVERITY_MAP[LogType(self.type)] + SEVERITY_MAP[LogLevel(self.level)]

    def __str__(self) -> str:
        return f'[{self.timestamp}] {self.level} {self.type}: {self.message}'

    def __repr__(self) -> str:
        return f'<LOG_{self.level_display}_{self.type}>'
