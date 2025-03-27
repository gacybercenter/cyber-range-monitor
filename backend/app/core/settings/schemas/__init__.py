from .app import AppConfig
from .extensions import RedisConfig, CORSPolicyConfig, DocumentationConfig
from .database import DatabaseConfig


settings_map = {
    "app": AppConfig,
    "database": DatabaseConfig,
    "redis": RedisConfig,
    "cors": CORSPolicyConfig,
    "documentation": DocumentationConfig
}

__all__ = [
    "AppConfig", 
    "DatabaseConfig", 
    "RedisConfig", 
    "CORSPolicyConfig",
    "DocumentationConfig",
    "settings_map"
]





