from re import S
from db.crud import CRUDService
from api.models import Log, LogType, LogLevel
from api.config.settings import app_config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.main.schemas import BaseLog, AppLog, SecurityLog, TracebackLog, LogResponse
from datetime import datetime


class LogService:
    _log_service = CRUDService(Log)

    @staticmethod
    async def _init(db: AsyncSession, model_dump: dict) -> None:
        await LogService._log_service.create(db, model_dump)

    @staticmethod
    async def traceback(db: AsyncSession, exc, exc_type) -> None:
        new_log = TracebackLog(
            message=str(exc),
            level=LogLevel.ERROR,
            type=LogType.TRACEBACK,
        )
        await LogService._init(db, new_log.model_dump())

    @staticmethod
    async def security(db: AsyncSession, msg: str, log_level: LogLevel) -> None:
        new_log = AppLog(
            message=msg,
            level=log_level,
            type=LogType.SECURITY
        )
        await LogService._init(db, new_log.model_dump())

    @staticmethod
    async def application(db: AsyncSession, msg: str, log_level: LogLevel) -> None:
        new_log = AppLog(
            message=msg,
            level=log_level,
            type=LogType.APPLICATION
        )
        await LogService._init(db, new_log.model_dump())

    @staticmethod
    async def get_by_id(log_id: str, db: AsyncSession) -> None:
        return await LogService._log_service.get_by(
            Log.id == log_id, db
        )

    @staticmethod
    async def get_by_level(log_level: LogLevel, db: AsyncSession) -> None:
        return await LogService._log_service.get_by(
            Log.level == log_level, db
        )

    @staticmethod
    async def logs_before(time: datetime, db: AsyncSession) -> None:
        return await LogService._log_service.get_by(Log.timestamp < time, db)

    @staticmethod
    async def order_by(log_prop, db: AsyncSession) -> list[LogResponse]:
        stment = select(Log).order_by(log_prop)
        result = await db.execute(stment)
        return list(result.scalars().all())

    @staticmethod
    async def log_message_like(expr: str, db: AsyncSession) -> None:
        return await LogService._log_service.get_by(
            Log.message.like(f"%{expr}%"), db
        )

    @staticmethod
    async def occured_on(date: datetime, db: AsyncSession) -> None:
        return await LogService._log_service.get_by(Log.timestamp == date, db)
