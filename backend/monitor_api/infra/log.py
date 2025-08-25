'''
Provides logging configuration for both stdlib logging,
and loguru with support for structured logging handling
correlation ids and the means to dispose of structured
loggers so that I/O resources are not leaked.

NOTE:
Loguru for some reason doesn't like being type hinted
for it's logger and record types, which is why they are
imported as such.
'''
from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from asgi_correlation_id import correlation_id
from loguru import logger as loguru_logger

from monitor_api.core import constant
from monitor_api.core.settings import get_adapter_settings

if TYPE_CHECKING:
    from loguru import Logger, Record



class InterceptHandler(logging.Handler):
    """
    Ensures stdlib logging goes through loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _cor_id_filter(record: 'Record') -> bool:
    """
    Ensures correlation_id is always present in the loguru record extras.

    Parameters
    ----------
    record : Record
    """
    record['correlation_id'] = correlation_id.get() # type: ignore[index]
    return record['correlation_id'] # type: ignore[return-value]


def _filter_by_name(name: str):

    def filter_fn(record: 'Record', _n=name) -> bool:
        return record['extra'].get('name') == _n

    return filter_fn


def _mute_noisy_loggers() -> None:
    noisy_loggers = ('uvicorn.error', 'uvicorn.access')
    for lname in noisy_loggers:
        logger = logging.getLogger(lname)
        logger.handlers = [InterceptHandler()]
        logger.propagate = False
        logger.setLevel(0)



def _file_sink_for(name: str) -> str:
    """
    Creates a dedicated sub directory with
    a timestamped of the log file for the
    structured logger with the given name.

    Parameters
    ----------
    name : str

    Returns
    -------
    str
    """
    directory = constant.LOGS_DIR_PATH / name
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / f'{name}_%Y-%m-%d.log')

def _error_filter(record: 'Record') -> bool:
    return record['level'].name in ('ERROR', 'CRITICAL')

@dataclass(slots=True)
class CustomLogLevel:
    name: str
    no: int
    color: str
    icon: str

    def filter(self, record: 'Record') -> bool:
        return record['level'].name == self.name



class _APILogger:
    CUSTOM_LOG_LEVELS: Final[Mapping[str, CustomLogLevel]] = {
        'SECURITY': CustomLogLevel(
            name='SECURITY',
            no=25,
            color='<yellow>',
            icon='🔐'
        ),
        'SERVICE': CustomLogLevel(
            name='SERVICE',
            no=15,
            color='<cyan>',
            icon='⚙️'
        ),
        'LIFESPAN': CustomLogLevel(
            name='LIFESPAN',
            no=12,
            color='<blue>',
            icon='⏳'
        ),
    }

    def __init__(self) -> None:
        self._sink_ids: dict[str, int] = {}


    def _add_file_logger(
        self,
        name: str,
        args: dict
    ) -> None:
        if name in self._sink_ids:
            return
        sink = _file_sink_for(name)
        sink_id = loguru_logger.add(
            sink,
            **args
        )
        self._sink_ids[name] = sink_id

    def _initialize(self) -> None:
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        _mute_noisy_loggers()
        loguru_logger.remove()

    def _add_custom_levels(self) -> None:
        for custom_level in self.CUSTOM_LOG_LEVELS.values():
            try:
                loguru_logger.level(
                    name=custom_level.name,
                    no=custom_level.no,
                    color=custom_level.color,
                    icon=custom_level.icon
                )
            except ValueError:
                continue


    def _add_stdout_logger(self) -> None:
        if 'stdout' in self._sink_ids:
            return
        config = get_adapter_settings().logging
        sink_id = loguru_logger.add(
            sys.stdout,
            level=config.level,
            filter=_cor_id_filter,
            colorize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False,
            format=constant.LOG_STDOUT_FORMAT,
            catch=True,
        )
        self._sink_ids['stdout'] = sink_id

    def _register_file_loggers(
        self,
        *,
        security_logger: bool = True,
        error_logger: bool = True,
        service_logger: bool = True,
    ) -> None:
        '''
        Registers the file loggers for the application.

        Parameters
        ----------
        security_logger : bool, optional
        error_logger : bool, optional
        service_logger : bool, optional
        '''
        config = get_adapter_settings().logging
        shared_kwargs = {
            'enqueue': True,
            'backtrace': False,
            'diagnose': False,
            'rotation': f'{config.rotation_mb} MB',
            'retention': f'{config.retention_days} days',
            'compression': config.compression,
            'serialize': True,
        }
        if security_logger:
            security_level = self.CUSTOM_LOG_LEVELS['SECURITY']
            self._add_file_logger(
                constant.SECURITY_LOGGER_NAME,
                {
                    **shared_kwargs,
                    'level': 'SECURITY',
                    'filter': security_level.filter,
                }
            )
        if error_logger:
            self._add_file_logger(
                constant.ERROR_LOGGER_NAME,
                {
                    **shared_kwargs,
                    'level': 'ERROR',
                    'filter': _error_filter,
                }
            )

        if service_logger:
            service_level = self.CUSTOM_LOG_LEVELS['SERVICE']
            self._add_file_logger(
                constant.SERVICE_LOGGER_NAME,
                {
                    **shared_kwargs,
                    'level': 'SERVICE',
                    'filter': service_level.filter,
                }
            )


    def dispose(self) -> None:
        for sink_id in self._sink_ids.values():
            loguru_logger.remove(sink_id)
        self._sink_ids.clear()

    def bind(self, **kwargs) -> 'Logger':
        """
        Returns a loguru logger instance with the given
        kwargs bound to the logger's context.

        Returns
        -------
        Logger
        """
        return loguru_logger.bind(**kwargs)

    def configure(
        self,
        *,
        stdout: bool = True,
        security_logger: bool = True,
        error_logger: bool = True,
        service_logger: bool = True,
    ) -> None:
        """
        Configures logging for the application and optionally
        a set of struct loggers.

        NOTE: To use struct logging, you must provide them in a
        dict in this method or you will not be able to retrieve them
        later. Provide the dict in the following format
        >>> {
            'my_struct_logger': 'DEBUG',
            'another_struct_logger': 'INFO',
            'yet_another_struct_logger': 20,
            }

        Parameters
        ----------
        stdout : bool, optional
            _Whether to log to stdout_, by default True
        security_logger : bool, optional
            _Whether to log security events to a dedicated file logger_,
            by default True
        error_logger : bool, optional
            _Whether to log errors to a dedicated file logger_,
            by default True
        service_logger : bool, optional
            _Whether to log service events to a dedicated file logger_,
            by default True
        """
        self._initialize()
        self._add_custom_levels()
        if stdout:
            self._add_stdout_logger()
        self._register_file_loggers(
            security_logger=security_logger,
            error_logger=error_logger,
            service_logger=service_logger,
        )

    def get_loguru_logger(self) -> 'Logger':
        """
        Returns a struct logger with the given name.

        Parameters
        ----------
        name : str

        Returns
        -------
        Logger
        """
        return loguru_logger



APILogger: Final[_APILogger] = _APILogger()