from datetime import timedelta
from typing import Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


DESC = (
    'An opensource API built with FastAPI to manage and monitor'
    'with support for Guacamole, Openstack and Saltstack datasources'
    'developed by the Georgia Cyber Range'
)

class AppConfig(BaseSettings):
    APP_ENV: str = Field('dev', description='Environment of the application')
    DESCRIPTION: str = Field(DESC, description='Description of the application')
    
    TITLE: str = 'Range Monitor v2 - API'
    VERSION: str = Field('dev', description='Version of the application')

    # ========================
    #       Flags
    # ========================
    
    DEBUG: bool = Field(False, description='Debug mode for the application')
    WRITE_LOGS: bool = Field(True, description='Write logs to the database')
    CONSOLE_LOG: bool = Field(False, description='Write event logs to the console or not')
    USE_SECURITY_HEADERS: bool = Field(True, description='Use the Security Header middleware for all requests, disable in dev')
    
    
    # ========================
    #       Secrets
    # ========================
    SECRET_KEY: str = Field(..., description='Secret key of the application')
    SIGNATURE_SALT: str = Field(..., description='Salt for the servers signature')
    ENCRYPTION_KEY: str = Field(..., description='Key for encrypting the session')
    RATE_LIMIT: str = Field('5/minute', description='Number of requests allowed per minute')
    CSRF_SECRET_KEY: str = Field(..., description='Key for CSRF protection')

    # ============================
    #       Documentation
    # ============================
    
    DOCS_OPENAPI_URL: Optional[str] = Field('/docs', description='URL for the API documentation')
    DOCS_OPENAPI_JSON_URL: Optional[str] = Field('/openapi.json', description='URL for the OpenAPI schema')
    DOCS_REDOC_URL: Optional[str] = Field('/redoc', description='URL for the ReDoc documentation')
    
    
    # ============================
    #  SQLite / SQLAlchemy Config
    # ============================
    
    DATABASE_URL: str = Field(..., description='URL for the database connection')
    DATABASE_ECHO: bool = Field(True, description='Echo SQL queries to stdout')

    # ============================
    #       Redis Config
    # ============================
    
    REDIS_DB: int = Field(0, description='Database number for redis')
    REDIS_HOST: str = Field('localhost', description='Host of the redis server')
    REDIS_PORT: int = Field(6379, description='Port of the redis server')
    REDIS_PASSWORD: str = Field('password', description='Password for the redis server')

    # ============================
    #       Cookie Config
    # ============================
    
    SESSION_COOKIE: str = Field('session_id', description='Name of the session cookie')
    COOKIE_SECURE: bool = Field(False, description='Secure flag for the cookie')
    COOKIE_HTTP_ONLY: bool = Field(False, description='HttpOnly flag for the cookie')
    COOKIE_SAMESITE: str = Field('lax', description='SameSite flag for the cookie')
    COOKIE_EXPIRATION_HOURS: int = Field(1, description='Lifetime of the session in seconds')
    SESSION_LIFETIME_DAYS: int = Field(1, description='Max age of the session in seconds')

    
class AppConfigMixin(AppConfig):
    def cookie_kwargs(self, cookie_value: Any) -> dict:
        return {
            'key': self.SESSION_COOKIE,
            'value': cookie_value,
            'samesite': self.COOKIE_SAMESITE,
            'secure': self.COOKIE_SECURE,
            'httponly': self.COOKIE_HTTP_ONLY,
            'max_age': self.cookie_expr()
        }

    def session_lifetime(self) -> int:
        return int(
            timedelta(days=self.SESSION_LIFETIME_DAYS).total_seconds()
        )

    def cookie_expr(self) -> int:
        return int(
            timedelta(hours=self.COOKIE_EXPIRATION_HOURS).total_seconds()
        )
