import logging
from logging.handlers import RotatingFileHandler

import os

from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install
from rich.console import Console
from rich.theme import Theme
from .const import (
    RICH_HANDLER_THEME,
    ERROR_LOG_FILE,
    LOG_DIR,
    CONSOLE_LOG_FORMAT,
    FILE_LOG_FORMAT,
    MAX_BYTES_LOG_FILE,
    SECURITY_LOG_FILE
)
from .config import log_settings
from app.core.settings import app_settings


def get_rich_handler() -> RichHandler:
    console = Console(
        theme=Theme(RICH_HANDLER_THEME)
    )
    handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_time=False,
        show_level=True,
        enable_link_path=True
    )

    handler.setFormatter(
        logging.Formatter(CONSOLE_LOG_FORMAT)
    )

    return handler


def get_file_handler(
    file_name: str,
    level: str
) -> RotatingFileHandler:
    '''Creates a file handler for logging to a file with rotation.

    Args:
        file_name (str): _the file name_
        level (str): _the log level to set_

    Returns:
        RotatingFileHandler: _the rotating file handler_
    '''
    handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, file_name),
        maxBytes=MAX_BYTES_LOG_FILE,
        delay=True
    )
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(FILE_LOG_FORMAT)
    )
    return handler


def configure_health_loggers() -> None:
    '''Configures the health loggers for the application and writes
    them to the log directory. This includes the error and security loggers.
    '''
    os.makedirs(LOG_DIR, exist_ok=True)

    error_logger = logging.getLogger('error')
    error_logger.setLevel('ERROR')
    error_logger.addHandler(get_file_handler(
        ERROR_LOG_FILE,
        'ERROR'
    ))

    security_logger = logging.getLogger('security')
    security_logger.setLevel('INFO')
    error_logger.addHandler(get_file_handler(
        SECURITY_LOG_FILE,
        'INFO'
    ))

    loggers = [
        error_logger,
        security_logger
    ]
    for logger in loggers:
        logger.propagate = False
        if app_settings.debug:
            logger.addHandler(get_rich_handler())


def setup_logging() -> None:
    '''Sets up logging for the application. This includes setting up the root logger.'''
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.setLevel(log_settings.log_level)
    if log_settings.stdout:
        rich_traceback_install(
            show_locals=True
        )
        root_logger.addHandler(get_rich_handler())
    configure_health_loggers()

    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.propagate = False
