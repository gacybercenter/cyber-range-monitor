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

import contextlib
import logging
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

from asgi_correlation_id import correlation_id
from loguru import logger as loguru_logger

from range_monitor import config, constant

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


class _LogFilters:
    @staticmethod
    def make_level_filter(level_name: str, no: int):
        def filter_fn(record: 'Record', _ln=level_name, _n=no) -> bool:
            return record['level'].name == _ln and record['level'].no == _n
        return filter_fn

    @staticmethod
    def error_filter(record: 'Record') -> bool:
        '''
        Filters loguru records to only allow ERROR and CRITICAL level logs.

        Parameters
        ----------
        record : Record
            _description_

        Returns
        -------
        bool
            _description_
        '''
        return (
            record['level'].name in ('ERROR', 'CRITICAL', 'EXCEPTION')
            and
            record['level'].no >= 40
        )

    @staticmethod
    def cor_id_filter(record: 'Record') -> bool:
        """
        Ensures correlation_id is always present in the loguru record extras.

        Parameters
        ----------
        record : Record
        """
        record['extra']['correlation_id'] = correlation_id.get() or 'N/A'
        return record['extra']['correlation_id'] # type: ignore[return-value]

class _LogSetup:

    @staticmethod
    def make_file_sink(name: str) -> str:
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


    @staticmethod
    def shared_file_log_args() -> dict:
        settings = config.get_app_settings()
        return {
            'enqueue': True,
            'backtrace': False,
            'diagnose': False,
            'rotation': f'{settings.logging.rotation_mb} MB',
            'retention': f'{settings.logging.retention_days} days',
            'compression': settings.logging.compression,
        }


    @staticmethod
    def reset_logging() -> None:
        '''
        Resets stdlib logging and ensures all loggers go through loguru.
        '''
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        noisy_loggers = ('uvicorn.error', 'uvicorn.access')
        for lname in noisy_loggers:
            logger = logging.getLogger(lname)
            logger.handlers = [InterceptHandler()]
            logger.propagate = False
            logger.setLevel(0)
        loguru_logger.remove()

    @staticmethod
    def error_filter(record: 'Record') -> bool:
        '''
        Filters loguru records to only allow ERROR and CRITICAL level logs.

        Parameters
        ----------
        record : Record
            _description_

        Returns
        -------
        bool
            _description_
        '''
        return (
            record['level'].name in ('ERROR', 'CRITICAL', 'EXCEPTION')
            and
            record['level'].no >= 40
        )


    @staticmethod
    def file_logger(
        *,
        name: str,
        level_no: int,
        file_options: dict,
        log_filter: Callable[['Record'], bool] | None = None,
    ) -> None:
        if log_filter is None:
            log_filter = _LogFilters.make_level_filter(name, level_no)

        file_sink = _LogSetup.make_file_sink(name.lower())
        loguru_logger.add(
            file_sink,
            level=name,
            filter=log_filter,
            **file_options,
        )



    @staticmethod
    def add_file_loggers(
        *,
        security_level_no: int,
        access_level_no: int,
    ) -> None:
        '''
        Sets up dedicated file loggers for each custom log level
        and also a dedicated error log file logger.

        Raises
        ------
        ValueError
            _If a custom log level does not have both `name` and `no` keys._
        '''

        common_file_options = _LogSetup.shared_file_log_args()

        loguru_logger.level(
            name='SECURITY',
            no=security_level_no,
            icon='🔐',
            color='<yellow>',
        )
        loguru_logger.level(
            name='ACCESS',
            no=access_level_no,
            icon='🛂',
            color='<cyan>',
        )

        _LogSetup.file_logger(
            name='SECURITY',
            level_no=security_level_no,
            file_options=common_file_options,
        )

        _LogSetup.file_logger(
            name='ACCESS',
            level_no=access_level_no,
            file_options=common_file_options,
        )

        _LogSetup.file_logger(
            name='ERROR',
            level_no=40,
            file_options=common_file_options,
            log_filter=_LogSetup.error_filter,
        )



    @staticmethod
    def setup_stdout_logger() -> None:
        '''
        Sets up the stdout logger for loguru.

        Parameters
        ----------
        level_name : str, optional
            _Name of the default level_, by default 'INFO'
        '''

        level = config.get_app_settings().logging.level
        loguru_logger.add(
            sys.stdout,
            level=level,
            filter=_LogFilters.cor_id_filter,
            colorize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False,
            format=constant.LOG_STDOUT_FORMAT,
            catch=True,
        )


def configure_logging(
    *,
    reset: bool = True,
    security_level_no: int = 25,
    access_level_no: int = 15,
) -> None:
    '''
    Configures logging for both stdlib logging and loguru.
    '''
    if reset:
        _LogSetup.reset_logging()

    _LogSetup.setup_stdout_logger()
    _LogSetup.add_file_loggers(
        security_level_no=security_level_no,
        access_level_no=access_level_no,
    )


def get_loguru_logger() -> 'Logger':
    '''
    Returns the loguru logger instance.

    Returns
    -------
    Logger
    '''
    return loguru_logger

def get_binded_logger(**kwargs) -> 'Logger':
    '''
    Returns a loguru logger instance with the given
    keyword arguments bound to it.

    Parameters
    ----------
    **kwargs
        Arbitrary keyword arguments to be bound to the logger.

    Returns
    -------
    Logger
    '''
    return loguru_logger.bind(**kwargs)


def create_access_log(
    *,
    message: str,
    **kwargs
) -> None:
    '''
    Logs an access log message at INFO level.

    Parameters
    ----------
    **kwargs
        Arbitrary keyword arguments to be logged.
    '''
    loguru_logger.log('ACCESS', message, **kwargs)

def create_security_log(
    *,
    message: str,
    **kwargs
) -> None:
    '''
    Logs a security log message at WARNING level.

    Parameters
    ----------
    **kwargs
        Arbitrary keyword arguments to be logged.
    '''
    loguru_logger.log('SECURITY', message, **kwargs)

@contextlib.contextmanager
def contextual_logger(**kwargs):
    with loguru_logger.contextualize(**kwargs):
        yield loguru_logger


def clear_sinks() -> None:
    '''
    Clears all loguru logger sinks.
    '''
    loguru_logger.remove()