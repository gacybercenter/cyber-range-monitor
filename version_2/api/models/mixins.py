from sqlalchemy import Column, DateTime, Integer, String, Boolean
from datetime import datetime, timezone


class AuditedMixin:
    '''Timestamps for created and updated at'''
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )


class DatasourceMixin:
    '''The shared columns for all of the Datasource models'''
    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    enabled = Column(Boolean, default=False)
    

    