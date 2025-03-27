from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db.base import BaseModel

from app.core.models import PkIDModelMixin

from .levels import EventLogLevel



class EventLog(BaseModel, PkIDModelMixin):
    __tablename__ = "event_logs"

    log_level: Mapped[EventLogLevel] = mapped_column(Enum(EventLogLevel), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __str__(self) -> str:
        return f"[ {self.log_level} ] | ({self.timestamp}) ] - {self.message}"

    def __repr__(self) -> str:
        return f"EventLog(log_level={self.log_level}, message={self.message}, timestamp={self.timestamp})"
