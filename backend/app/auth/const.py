from app.configs import SessionConfig, SESSION_ENV_PREFIX, config_init
from .session_security import SessionIdAuthority

SESSION_CONFIG = SessionConfig(
    **config_init(SESSION_ENV_PREFIX)
)
SESSION_COOKIE_BEARER = SessionIdAuthority()