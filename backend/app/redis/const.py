
# NOTE: These are the constants used for the Redis connection and socket settings.
# change as the requirements and users of the app increase.
import re

from fastapi import status


SOCKET_CONNECT_TIMEOUT: float = 1.0
SOCKET_TIMEOUT: float = 5.0
MAX_CONNECTIONS: int = 10

# sanitization consts
MAX_KEY_LENGTH: int = 512

VALID_KEY_RE = re.compile(r"[a-zA-Z0-9\.\-\_\:]+$")

KEY_INJECTION_RE = re.compile(
    r'(FLUSHALL|FLUSHDB|DEL\s|CONFIG|EVAL|SCRIPT|KEYS\s|\s|\{|\}|\[|\]|\'|\"|\`|\;|\|)'
)

