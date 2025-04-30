
RICH_HANDLER_THEME = {
    'debug': 'dim cyan',
    'info': 'green',
    'warning': 'yellow',
    'error': 'bold red',
    'critical': 'bold white on red',
}

LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

CONSOLE_LOG_FORMAT = (
    "[ %(asctime)s ] [bold blue]%(name)s[/bold blue] "
    "[bold red]~[/bold red][bold blue]$[/bold blue] [italic white]%(message)s[/italic white]\n"
)

FILE_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d | pid:%(process)d | tid:%(threadName)s "
    "- [ %(name)s - %(levelname)s ]: %(message)s"
)

LOG_DIR = 'logs'

ERROR_LOG_FILE = 'error.log'
SECURITY_LOG_FILE = 'security.log'

MAX_BYTES_LOG_FILE = (1024 * 1024) * 10  # 10 MB
