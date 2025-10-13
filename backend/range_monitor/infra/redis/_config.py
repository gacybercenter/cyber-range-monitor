from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import EnvConfig, TomlSection


class RedisConfig(EnvConfig):
    """in env file as redis_<attribute>"""

    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    username: str | None = None
    password: str | None = None
    ssl: bool = False


class RedisOptions(TomlSection):
    """config.toml -> [redis]"""

    socket_connect_timeout: float = 5
    retry_on_timeout: bool = True
    health_check_interval: float = 10
    max_connections: int = 10
    socket_keepalive: bool = True
    socket_timeout: float = 5
