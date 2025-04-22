import logging

import os

from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install
from rich.console import Console
from rich.theme import Theme

from app import config

from .const import (
    LOG_THEME,
    APP_LOGGER,
    SERVICE_LOGGER,
    MIDDLEWARE_LOGGER,
    LOG_FORMAT,
    LOG_FILE_DIR,
    REQUEST_LOGGER
)


log_config = config.get_config_yml().logging


class APILogging:
    '''singleton class for managing logging throughout the application'''
    _instance: 'APILogging' = None  # type: ignore[assignment]
    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def setup(cls) -> logging.Logger:
        '''setups and configures the most important
        loggers for the application and returns the top level
        or 'api' logger

        Returns:
            logging.Logger -- the configure api logger
        '''
        if cls._instance:
            return cls.api()

        cls._instance = cls()

        os.makedirs(LOG_FILE_DIR, exist_ok=True)
        root_logger = logging.getLogger()
        root_logger.setLevel(log_config.api_level)

        cls._configure_root_logger(root_logger)
        configs = get_known_loggers()
        for conf in configs:
            name, level, file = conf
            print('\n\nConfiguring logger:', name)
            configure_logger(name, file, level)

        api = cls.api()
        api.info('\n\nLogging setup complete\n\n')

        return api

    @classmethod
    def _configure_root_logger(cls, root_logger: logging.Logger) -> None:
        '''configures top level logger

        Arguments:
            root_logger {logging.Logger} -- the top level logger
        '''
        log_stdout = Console(theme=Theme(LOG_THEME))

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        rich_handler = RichHandler(
            console=log_stdout,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
            show_time=False,
            show_level=True,
            enable_link_path=True
        )

        rich_traceback_install(
            show_locals=True
        )

        root_logger.addHandler(rich_handler)

    @classmethod
    def disable_uvicorn_logger(cls) -> None:
        '''disables the uvicorn logger'''
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    @classmethod
    def middleware(cls) -> logging.Logger:
        return logging.getLogger(MIDDLEWARE_LOGGER)

    @classmethod
    def service(cls) -> logging.Logger:
        return logging.getLogger(SERVICE_LOGGER)

    @classmethod
    def api(cls) -> logging.Logger:
        return logging.getLogger(APP_LOGGER)

    @classmethod
    def requests(cls) -> logging.Logger:
        return logging.getLogger(REQUEST_LOGGER)


def get_known_loggers() -> list[tuple[str, str, str]]:
    # adjust this if you add a new logger
    api_level, service_level, middleware_level = (
        log_config.api_level,
        log_config.service_level,
        log_config.middleware_level
    )
    known_loggers = [
        (APP_LOGGER, api_level, 'app.log'),
        (SERVICE_LOGGER, service_level, 'service.log'),
        (MIDDLEWARE_LOGGER, middleware_level, 'middleware.log'),
        (REQUEST_LOGGER, 'INFO', 'requests.log')
    ]
    return known_loggers


def configure_logger(name: str, file: str, level: str) -> logging.Logger:
    '''configures a logger for the application

    Arguments:
        name {str} -- the name of the logger
        file {str} -- the file name of the logger
        level {str} -- the level of the logger

    Returns:
        logging.Logger -- the configured logger
    '''
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)
    if not log_config.allow_file_handler:
        return logger

    file_handler = logging.FileHandler(os.path.join(LOG_FILE_DIR, file))
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger
