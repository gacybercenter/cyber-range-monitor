import logging
from logging.handlers import RotatingFileHandler

import os
from typing import Optional

from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install
from rich.console import Console
from rich.theme import Theme


from .const import (
    RICH_HANDLER_THEME,
    ERROR_LOG_FILE,
    LOG_DIR,
    LOG_FORMAT,
    MAX_BYTES_LOG_FILE,
    SECURITY_LOG_FILE
)
from .config import log_settings


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
    return handler


def add_file_handler(
    logger: logging.Logger,
    file_name: str,
    level: str
) -> None:
    handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, file_name),
        maxBytes=MAX_BYTES_LOG_FILE,
        delay=True
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


def add_stdout_handler(
    logger: logging.Logger,
    use_rich: bool,
    level: str
) -> None:
    if not use_rich:
        handler = logging.StreamHandler()
    else:
        handler = get_rich_handler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


def configure_logger(
    name: str,
    stdout: bool = True,
    stdout_level: str = 'WARNING',
    use_rich: bool = True,
    log_file: Optional[str] = None,
    file_level: str = 'INFO'
) -> None:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    if stdout:
        add_stdout_handler(
            logger=logger,
            use_rich=use_rich,
            level=stdout_level
        )

    if log_file:
        add_file_handler(
            logger=logger,
            file_name=log_file,
            level=file_level
        )


def setup_logging() -> None:
    if log_settings.use_rich:
        rich_traceback_install(
            show_locals=True
        )
    os.makedirs(LOG_DIR, exist_ok=True)
    configure_logger(
        name='app',
        stdout=log_settings.stdout,
        use_rich=log_settings.use_rich,
        stdout_level=log_settings.stdout_level,
        file_level=log_settings.file_log_level,
        log_file='app.log'
    )

    configure_logger(
        name='security',
        stdout=log_settings.stdout,
        use_rich=log_settings.use_rich,
        stdout_level='INFO',
        file_level='INFO',
        log_file=SECURITY_LOG_FILE,
    )

    configure_logger(
        name='error',
        use_rich=False,
        stdout=True,
        stdout_level='ERROR',
        file_level='ERROR',
        log_file=ERROR_LOG_FILE
    )


def get_security_logger() -> logging.Logger:
    return logging.getLogger('security')


def get_error_logger() -> logging.Logger:
    return logging.getLogger('error')
