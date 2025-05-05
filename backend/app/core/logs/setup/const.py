
import logging.config
RICH_THEME = {
    'debug': 'dim cyan',
    'info': 'green',
    'warning': 'yellow',
    'error': 'bold red',
    'critical': 'bold white on red',
}

STDOUT_LOG_FORMAT = "[ %(asctime)s ] monitor_api@%(name)s~$ %(message)s | %(levelname)s"

FILE_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d | pid:%(process)d | tid:%(threadName)s "
    "- [ %(name)s - %(levelname)s ]: %(message)s"
)

