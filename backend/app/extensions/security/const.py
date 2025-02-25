from app.configs import SecretsConfig, SECRETS_ENV_PREFIX, config_init


SECRET_CONFIG = SecretsConfig(
    **config_init(SECRETS_ENV_PREFIX)
)