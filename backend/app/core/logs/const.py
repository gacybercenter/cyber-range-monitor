
RICH_HANDLER_THEME = {
    'debug': 'dim cyan',
    'info': 'green',
    'warning': 'yellow',
    'error': 'bold red',
    'critical': 'bold white on red',
}

LOG_DATE = 'time:YYYY-MM-DD HH:mm:ss.SSS'
LOG_FORMAT = '{LOG_DATE} - [ %(name)s - %(levelname)s ]: %(message)s'
LOG_DIR = 'logs'
ERROR_LOG_FILE = 'error.log'

SECURITY_LOG_FILE = 'security.log'

MAX_BYTES_LOG_FILE = (1024 * 1024) * 10  # 10 MB