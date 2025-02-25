from app.configs import RedisConfig, REDIS_ENV_PREFIX, config_init


REDIS_CONFIG = RedisConfig(
    **config_init(REDIS_ENV_PREFIX)
)
