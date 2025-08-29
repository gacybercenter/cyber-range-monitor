from datetime import timedelta
from typing import Final

SESSION_MAX_AGE: Final[timedelta] = timedelta(days=1)
SESSION_IDLE_TIMEOUT: Final[timedelta] = timedelta(hours=1)


BEARER_DESCRIPTION: Final[str] = (
    'OAuth2 authentication scheme that uses a signed session ID as the token. '
    'As a dependency, it extracts the token from the Authorization header, '
    'validates the signature and checks if the max age has been reached '
    'for idle timeouts, perform additional checks'
)
BEARER_SCHEME_NAME: Final[str] = 'Session ID Bearer'