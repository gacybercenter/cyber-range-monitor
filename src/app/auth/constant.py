from ..security import SessionAuthority
from .config import SessionConfig


SESSION_KEY = 'session:'
SESSION_CONFIG = SessionConfig() # type: ignore
SESSION_AUTHORITY = SessionAuthority(SESSION_CONFIG.SESSION_COOKIE)