from .app import AppConfig
from .core import RedisConfig, CORSPolicyConfig, DatabaseConfig
from .logs import LogsConfig


settings_map = {
    "app": AppConfig,
    "database": DatabaseConfig,
    "redis": RedisConfig,
    "cors": CORSPolicyConfig,
    "logging": LogsConfig
}

__all__ = [
    "AppConfig",
    "DatabaseConfig",
    "RedisConfig",
    "CORSPolicyConfig",
    "settings_map",
    "LogsConfig",
]
