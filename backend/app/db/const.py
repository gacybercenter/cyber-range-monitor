from app.configs import DatabaseConfig, DATABASE_ENV_PREFIX, config_init


DATABASE_CONFIG = DatabaseConfig(
    **config_init(DATABASE_ENV_PREFIX)
)
