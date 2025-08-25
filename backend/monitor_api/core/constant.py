from pathlib import Path
from typing import Final

ROOT_PATH: Final[Path] = Path(__file__).parent.parent.parent.resolve()

LOGS_DIRNAME: Final[str] = 'logs'

LOGS_DIR_PATH: Final[Path] = ROOT_PATH / LOGS_DIRNAME

DATABASE_DIRNAME: Final[str] = 'instance'

DATABASE_DIR_PATH: Final[Path] = ROOT_PATH / DATABASE_DIRNAME


LOG_STDOUT_FORMAT: Final[str] = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    'cid=<cyan>{extra[correlation_id]}</cyan> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
    '<level>{message}</level>'
)

SECURITY_LOGGER_NAME: Final[str] = 'security'
ERROR_LOGGER_NAME: Final[str] = 'error'
SERVICE_LOGGER_NAME: Final[str] = 'service'

APP_TITLE: Final[str] = 'Range Monitor API'
APP_DESCRIPTION: Final[str] = (
    'The backend application for Cyber Range Monitor, powered by FastAPI. '
    'Authentication is session-based and you can authenticate using the session ID'
    ' returned upon login and authenticate with the `Authorization` header or click '
    'the lock icon in the Swagger UI and enter the session ID there.'
)
APP_SUMMARY: Final[str] = 'The backend for the Range Monitor'

REQUEST_ID_HEADER_NAME: Final[str] = 'X-Request-ID'
REQUEST_IP_HEADER_NAME: Final[str] = 'X-Forwarded-For'
NOISEY_LOGGERS: Final[tuple[str, ...]] = (
    'uvicorn.access',
    'uvicorn.error',
)

OPENAPI_URL: Final[str] = '/openapi.json'
DOCS_URL: Final[str] = '/docs'
REDOC_URL: Final[str] = '/redoc'