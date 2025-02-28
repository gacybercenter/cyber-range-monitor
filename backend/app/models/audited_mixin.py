from datetime import datetime, timezone

from sqlalchemy import Column, DateTime


class AuditedMixin(object):
    '''Timestamps for created and updated at'''
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
