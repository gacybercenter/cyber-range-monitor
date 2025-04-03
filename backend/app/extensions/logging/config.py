import logging
import sys
from typing import Literal
from pathlib import Path


from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install


LogLevel = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']


def setup_api_logging(log_level: LogLevel = 'INFO', log_file: Path | None = None) -> None:
    '''sets up logs outside of the database for general application logging

    Keyword Arguments:
        log_level {str} -- the log level (default: {'INFO'})
        log_file {Path | None} -- _description_ (default: {None})
    '''
    from app.extensions.api_console import get_console

    rich_handler = RichHandler(
        console=get_console(),
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_time=True,
        show_level=True,
        enable_link_path=True
    )

    rich_traceback_install(
        show_locals=True
    )

    logging.basicConfig(
        level=log_level.upper(),
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[rich_handler]
    )

    if log_file:
        _setup_file_logger(log_level, log_file)

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.propagate = True


def _setup_file_logger(level: str, log_file: Path) -> None:
    '''setups the file logger for the application

    Arguments:
        level {str} -- the level of the log
        log_file {Path} -- the path to the log file
    '''
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level.upper())
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
