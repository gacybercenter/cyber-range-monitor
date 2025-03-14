from .app import AppConfig
from .extensions import AuthConfig, RedisConfig, CORSPolicyConfig, DocumentationConfig
from .database import DatabaseConfig


settings_map = {
    "app": AppConfig,
    "database": DatabaseConfig,
    "redis": RedisConfig,
    "auth": AuthConfig,
    "cors": CORSPolicyConfig,
    "documentation": DocumentationConfig
}

__all__ = [
    "AppConfig", 
    "DatabaseConfig", 
    "RedisConfig", 
    "AuthConfig", 
    "CORSPolicyConfig",
    "DocumentationConfig",
    "settings_map"
]





