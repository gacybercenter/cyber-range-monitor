import logging
import os
from typing import List


from rich.traceback import install as install_rich_traceback

from . import setup
from .config import log_settings
from .const import APP_LOG_FILE, LOG_DIR


def setup_loggers() -> None:
    """setups the root logger with the settings from the config file."""

    app_logger = logging.getLogger('app')
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    os.makedirs(name=LOG_DIR, exist_ok=True)
    if log_settings.use_rich:
        install_rich_traceback(
            show_locals=True
        )

    console_handler = setup.create_stdout_handler(
        use_rich=log_settings.use_rich,
        level=log_settings.log_levels.stdout
    )

    file_handler = setup.create_file_handler(
        file_path=os.path.join(LOG_DIR, APP_LOG_FILE),
        level=log_settings.log_levels.file,
        max_bytes=log_settings.file_size
    )

    app_logger.addHandler(console_handler)
    app_logger.addHandler(file_handler)

    setup.configure_uvicorn_logger(
        level=log_settings.log_levels.uvicorn,
        uvicorn_audit=log_settings.uvicorn_audit,
        max_bytes=log_settings.file_size
    )


def websocket_loggers() -> List[str]:
    """returns the loggers that are enabled for websocket logging."""
    return log_settings.websocket_loggers
