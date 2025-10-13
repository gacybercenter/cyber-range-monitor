import os
import sys

from range_monitor.infra.security import utils as security_utils
from range_monitor.infra.security._config import CryptoConfig, JwtSecrets


def is_okay_to_override() -> bool:
    return input('.env file already exists. Override? (y/N): ').lower() == 'y'


def generate_secrets() -> dict:
    jwt_env = JwtSecrets(jwt_secret_key=security_utils.generate_secret_key())
    fernet_key = security_utils.generate_fernet_key()
    crypto_env = CryptoConfig(
        fernet_key=fernet_key, bcrypt_pepper=security_utils.generate_secret_key(16)
    )
    return {
        **jwt_env.model_dump(),
        **crypto_env.model_dump(),
    }


def main() -> None:
    print("""
    *********************
    scripts.create_env
    *********************
    Usage: python scripts/create_env.py [env_file | default: .env]
    """)

    if len(sys.argv) > 1:
        env_path = sys.argv[1]
    else:
        env_path = '.env'

    env_content = generate_secrets()
    if os.path.exists(env_path) and not is_okay_to_override():
        print('Aborting .env creation.')
        return

    print('Creating .env file with generated secrets...')
    with open(env_path, 'w') as f:
        for key, value in env_content.items():
            f.write(f'{key}={value}\n')


if __name__ == '__main__':
    main()
