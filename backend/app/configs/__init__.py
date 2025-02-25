from .main import running_app_config, running_project, config_init
from .session import SessionConfig, SESSION_ENV_PREFIX
from .redis import RedisConfig, REDIS_ENV_PREFIX
from .secret import SecretsConfig, SECRETS_ENV_PREFIX
from .database import DatabaseConfig, DATABASE_ENV_PREFIX


CONFIG_MAP = {
    'app': {
        'env_prefix': 'n/a',
        'config': running_app_config(),
    },
    'project': {
        'env_prefix': 'n/a',
        'config': running_project()
    },
    'session': {
        'config': SessionConfig,
        'env_prefix': SESSION_ENV_PREFIX
    },
    'redis': {
        'config': RedisConfig,
        'env_prefix': REDIS_ENV_PREFIX
    },
    'secrets': {
        'config': SecretsConfig,
        'env_prefix': SECRETS_ENV_PREFIX
    },
    'database': {
        'config': DatabaseConfig,
        'env_prefix': DATABASE_ENV_PREFIX
    }
}



















