from typing import Annotated

from fastapi import Depends

from app.db.dependency import DatabaseRequired

from .service import LogService


async def get_log_controller(db: DatabaseRequired) -> LogService:
    """Creates a LogService instance with the database session"""
    return LogService(db)


LogController = Annotated[LogService, Depends(get_log_controller)]
