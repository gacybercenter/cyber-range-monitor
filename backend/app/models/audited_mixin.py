from datetime import UTC, datetime

from sqlalchemy import Column, DateTime


class AuditedMixin:
    """Timestamps for created and updated at"""

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
