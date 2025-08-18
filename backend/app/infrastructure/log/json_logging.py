from __future__ import annotations

import atexit
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from app.core import path_utils
from app.core.singletons import SingletonMeta

from .settings import log_settings
from .utils import get_loguru_logger, inject_asgi_correlation_id

if TYPE_CHECKING:
    from loguru import Logger


def _get_file_logger_dir(logger_name: str) -> Path:
    logger_dir = path_utils.get_app_root().joinpath(log_settings.directory, logger_name)
    logger_dir.mkdir(parents=True, exist_ok=True)

    return logger_dir


def _file_log_pattern(directory: Path, logger_name: str) -> str:
    timestamp = '{time:YYYY-MM-DD}'
    return str(directory.joinpath(f'{logger_name}_{timestamp}.log'))


@dataclass(slots=True)
class JsonLogger:
    bind: object
    sink_id: int

    def close(self) -> None:
        """
        Disposes the logger by removing its sink to prevent memory leaks
        """
        try:
            if hasattr(self, 'sink_id'):
                self.bind.remove(self.sink_id) # type: ignore
                delattr(self, 'sink_id')
        except Exception:
            pass

    @property
    def logger(self) -> 'Logger':
        """
        Returns the logger instance.
        """
        return self.bind # type: ignore


def create_json_log(name: str, level: str = 'INFO') -> JsonLogger:
    """
    Creates a JSON logger with the specified name and level.

    Parameters
    ----------
    name : str
    level : str, optional

    Returns
    -------
    JsonLog
    """
    directory = _get_file_logger_dir(name)
    sink = _file_log_pattern(directory, name)
    bind = get_loguru_logger().bind(component=name)
    sink_id = get_loguru_logger().add(
        sink,
        level=level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        rotation=f'{log_settings.rotation_mb} MB',
        retention=f'{log_settings.retention_days} days',
        compression=log_settings.compression,
        serialize=True,
        filter=inject_asgi_correlation_id,
    )
    return JsonLogger(bind=bind, sink_id=sink_id)

class JsonLogContext(metaclass=SingletonMeta):
    '''
    Singleton for managaing JSON loggers and guarntees that
    the logger shut downs are performed on exit
    '''

    def __init__(self) -> None:
        self.__context: dict[str, JsonLogger] = {}


    def add_logger(self, name: str, level: str) -> None:
        """
        Adds a new logger to the registry.

        Parameters
        ----------
        name : str
            The name of the logger.
        level : str
            The logging level for the logger.
        """
        if name in self.__context:
            raise RuntimeError(f'Logger with name {name} is already registered.')

        logger = create_json_log(name, level)
        self.__context[name] = logger

    def register(self, name: str, level: str) -> 'Logger':
        """
        Registers a new JSON logger with the specified name and level.

        Parameters
        ----------
        name : str
            The name of the logger.
        level : str
            The logging level for the logger.
        """
        self.add_logger(name, level)
        return self.__context[name].logger

    def get_logger(self, name: str) -> 'Logger':
        if name not in self.__context:
            raise KeyError(f'Logger with name {name} does not exist.')
        return self.__context[name].logger

    def dispose(self) -> None:
        """
        Closes all loggers in the registry.
        """
        for logger in self.__context.values():
            logger.close()
        self.__context.clear()


JSONLogContext: Final[JsonLogContext] = JsonLogContext()


def setup_json_logging() -> None:
    """
    Sets up the JSON loggers based on the configuration in
    `log_settings`.
    """
    if not log_settings.json_loggers:
        return
    global JSONLogContext
    registry = JSONLogContext
    for options in log_settings.json_loggers:
        registry.register(name=options.name, level=options.level)

    atexit.register(registry.dispose)

def get_json_logger() -> JsonLogContext:
    """
    Returns the singleton instance of the JSON logger manager.
    """
    return JsonLogContext()
