from datetime import timedelta
from typing import Any, Literal

import httpx
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from server.configs.sources import Config, get_toml_config_source


class LoggerConfig(Config):
    '''
    Logger configuration settings.
    '''

    format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "cid=<cyan>{extra[correlation_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    level: str = "DEBUG"
    structured_stdout: bool = True
    enqueue: bool = True
    backtrace: bool = True
    diagnose: bool = False
    colorize: bool = True


class CorsConfig(Config):
    '''
    CORS configuration settings.
    '''
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class SqlalchemyConfig(Config):
    '''
    SQLAlchemy engine configuration options.
    '''

    echo: bool = Field(
        default=False,
        description="If True, the engine will log all statements."
    )
    timeout: int = Field(
        default=30,
        description="The timeout for database connections in seconds."
    )
    autoflush: bool = Field(
        default=True,
        description="If True, the session will autoflush before queries."
    )
    expire_on_commit: bool = Field(
        default=False,
        description="If True, all instances will be expired after each commit.",
    )
    pool_pre_ping: bool = Field(
        default=True,
        description="If True, the engine will test connections upon each checkout.",
    )
    pool_recycle: int = Field(
        default=1800,
        description="The number of seconds after which a connection is recycled.",
    )
    pool_size: int = Field(
        default=10,
        description="The size of the database connection pool."
    )
    max_overflow: int = Field(
        default=20,
        description="The maximum overflow size of the database connection pool.",
    )
    future: Literal[True] = Field(
        default=True,
        description="If True, use SQLAlchemy 2.0 style engine and connection behavior.",
    )


class RedisConfig(Config):
    '''
    Options for configuring the Redis client connection.
    '''

    socket_connect_timeout: int = Field(
        default=5, description="Timeout for connecting to Redis server in seconds"
    )
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout errors")
    max_connections: int = Field(
        default=10, description="Maximum number of connections in the pool"
    )
    socket_keepalive: bool = Field(default=True, description="Enable TCP keepalive")
    decode_responses: bool = Field(
        default=True, description="Decode responses to strings"
    )
    health_check_interval: int = Field(
        default=30, description="Interval for health checks in seconds"
    )
    socket_timeout: int = Field(default=5, description="Socket timeout in seconds")


class AuthenticationConfig(Config):
    '''
    Authentication configuration settings.
    '''

    access_token_minutes: int = Field(default=30, gt=1)
    refresh_token_hours: int = Field(gt=1, default=24)
    jwt_issuer: str = Field(
        default="range-monitor",
        description="The issuer claim for JWT tokens.",
    )
    jwt_audience: str = Field(
        default="range-monitor-users",
        description="The audience claim for JWT tokens.",
    )
    token_leeway_seconds: int = Field(
        default=60,
        description="The leeway time in seconds for JWT clock skew.",
    )
    csrf_token_exp_minutes: int = Field(
        default=10,
        gt=1,
        description="The expiration time in minutes for CSRF tokens.",
    )
    cookie_secure: bool = Field(
        default=True,
        description="Whether cookies should be marked as secure.",
    )
    cookie_httponly: bool = Field(
        default=True,
        description="Whether cookies should be marked as HttpOnly.",
    )
    cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="The SameSite attribute for cookies.",
    )
    cookie_domain: str | None = Field(
        default=None,
        description="The domain attribute for cookies.",
    )

    @property
    def access_token_exp(self) -> timedelta:
        return timedelta(minutes=self.access_token_minutes)

    @property
    def refresh_token_exp(self) -> timedelta:
        return timedelta(hours=self.refresh_token_hours)

    @property
    def csrf_token_exp(self) -> timedelta:
        return timedelta(minutes=self.csrf_token_exp_minutes)


class HttpxConfig(Config):
    '''
    HTTPX client configuration options.
    '''

    limit_max_keepalive_connections: int = Field(
        default=5,
        description="The max number of keep-alive connections."
    )
    limit_max_connections: int = Field(
        default=50,
        description="The max number of connections."
    )
    limit_keepalive_expiry: int = Field(
        default=30,
        description="The keep-alive expiry time in seconds."
    )
    connect_timeout: float = Field(
        default=5.0,
        description="The max time to wait for a connection to be established.",
    )
    read_timeout: float = Field(
        default=10.0,
        description="The max time to wait for a read operation to complete.",
    )
    write_timeout: float = Field(
        default=10.0,
        description="The max time to wait for a write operation to complete.",
    )
    pool_timeout: float = Field(
        default=5.0,
        description="The max time to wait for acquiring a connection from the pool.",
    )
    max_redirects: int = Field(
        default=5, description="The maximum number of redirects to follow."
    )
    http2: bool = Field(default=True, description="Enable HTTP/2 support.")

    def dump_httpx_opts(self) -> dict[str, Any]:
        return {
            "limits": httpx.Limits(
                max_keepalive_connections=self.limit_max_keepalive_connections,
                max_connections=self.limit_max_connections,
                keepalive_expiry=self.limit_keepalive_expiry,
            ),
            "timeout": httpx.Timeout(
                connect=self.connect_timeout,
                read=self.read_timeout,
                write=self.write_timeout,
                pool=self.pool_timeout,
            ),
            "max_redirects": self.max_redirects,
            "http2": self.http2,
        }


class AppConfig(Config):
    '''
    Application configuration settings.
    '''

    title: str = Field(
        default="Range Monitor Backend API",
        description="The title of the application",
    )
    description: str = Field(
        default="The backend ASGI FastAPI application for the Range Monitor",
        description="A detailed description of the application",
    )
    summary: str = Field(
        default="The backend ASGI FastAPI application for the Range Monitor",
        description="A short summary of the application",
    )
    version: str = Field(default="0.1.0", description="The application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    testing: bool = Field(default=False, description="Enable testing mode")
    allow_docs: bool = Field(
        default=True,
        description="Allow documentation routes, e.g. /docs, /redoc, /openapi.json",
    )
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"


class AppTomlSettings(Config):
    '''config.toml'''
    app: AppConfig = Field(default_factory=AppConfig)
    logger: LoggerConfig = Field(default_factory=LoggerConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    httpx: HttpxConfig = Field(default_factory=HttpxConfig)
    auth: AuthenticationConfig = Field(default_factory=AuthenticationConfig)
    sql_alchemy: SqlalchemyConfig = Field(default_factory=SqlalchemyConfig)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='APP_',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        toml_source = get_toml_config_source(settings_cls)
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            toml_source,
            file_secret_settings,
        )
