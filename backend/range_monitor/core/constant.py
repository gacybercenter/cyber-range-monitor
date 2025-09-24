from pathlib import Path
from typing import Final

APP_PATH: Final[Path] = Path(__file__).parent.parent.resolve()
APP_ROOT_PATH: Final[Path] = APP_PATH.parent.resolve()

DATABASE_DIRNAME: Final[str] = 'sqlite'
LOGS_DIRNAME: Final[str] = 'logs'
DATABASE_DRIVERNAME: Final[str] = 'sqlite+aiosqlite'
DATABASE_FILENAME: Final[str] = 'range_monitor.sqlite3.db'

DATABASE_DIR_PATH: Final[Path] = APP_ROOT_PATH / DATABASE_DIRNAME
LOGS_DIR_PATH: Final[Path] = APP_ROOT_PATH / LOGS_DIRNAME