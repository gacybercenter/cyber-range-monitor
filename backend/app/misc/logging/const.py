

# names of the handlers, makes it easy if the names ever change or a conflict occurs


LOG_THEME = {
    'debug': 'dim cyan',
    'info': 'green',
    'warning': 'yellow',
    'error': 'bold red',
    'critical': 'bold white on red',
}

APP_LOGGER = 'api'

SERVICE_LOGGER = 'api.service'

MIDDLEWARE_LOGGER = 'api.middleware'

AUTH_LOGGER = 'api.auth'

LOG_FORMAT = '[ %(asctime)s | %(levelname)-5s ] - %(message)s (@%(name)s->%(filename)s:%(lineno)d)'

LOG_FILE_DIR = 'logs'

REQUEST_LOGGER = 'api.requests'
