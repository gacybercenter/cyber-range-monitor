from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from .config_init import settings_config


SESSION_ENV_PREFIX = 'SESSION_'
class SessionConfig(BaseSettings):
    '''The configuration settings for the session cookie_
    '''
    COOKIE_NAME: str = Field(
        'session_id',
        description='Name of the session cookie'
    )
    COOKIE_SECURE: bool = Field(
        False,
        description='Secure flag for the cookie'
    )
    COOKIE_HTTP_ONLY: bool = Field(
        False,
        description='HttpOnly flag for the cookie'
    )
    COOKIE_SAMESITE: str = Field(
        'lax',
        description='SameSite flag for the cookie'
    )
    COOKIE_EXPR_HOURS: int = Field(
        1,
        description='Lifetime of the session in seconds before it is deleted on the client'
    )
    SESSION_LIFETIME_DAYS: int = Field(
        1,
        description='Max age of a session in seconds before the user must re-authenticate'
    )
    
    model_config = settings_config(SESSION_ENV_PREFIX)
    
    
    def cookie_expiration(self) -> int:
        '''converts the cookie expiration hours to seconds'''
        return self.COOKIE_EXPR_HOURS * 60 * 60

    def cookie_kwargs(self, cookie_value: str) -> dict:
        '''given a cookie value, the api issues the cookie 
        with the set configurations in the settings (reduces typing)

        Arguments:
            cookie_value {str} -- the value of the cookie

        Returns:
            dict -- the kwargs for issuing the cookie
        '''
        return {
            'key': self.COOKIE_NAME,
            'value': cookie_value,
            'samesite': self.COOKIE_SAMESITE,
            'secure': self.COOKIE_SECURE,
            'httponly': self.COOKIE_HTTP_ONLY,
            'max_age': self.cookie_expiration()
        }

    def session_max_age(self) -> int:
        '''converts the session lifetime days to seconds
        Returns:
            int -- the session lifetime in seconds
        '''
        return self.SESSION_LIFETIME_DAYS * 24 * 60 * 60

    