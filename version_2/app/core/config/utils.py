from .app_config import (
    BuildConfig,
    RedisConfig,
    DatabaseConfig,
    SessionConfig,
    DocumentationConfig,
    BaseAppConfig,
    config_prefixes
)
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path
from dotenv import dotenv_values
from pydantic import ValidationError


class EnvironIO:
    ENV_DIR: Path = Path(".environment")

    @staticmethod
    def list_environs() -> list[Path]:
        if not EnvironIO.ENV_DIR.exists():
            return []
        return list(EnvironIO.ENV_DIR.glob("*.env"))

    @staticmethod
    def load_env(env_name: str) -> dict:
        env_file = EnvironIO.env_path(env_name)

        if not env_file.exists():
            raise FileNotFoundError(
                f"No environment file found: {env_name}.env"
            )

        return dict(dotenv_values(env_file))

    @staticmethod
    def env_path(env_name: str) -> Path:
        return EnvironIO.ENV_DIR / f"{env_name}.env"

    @staticmethod
    def env_exists(env_name: str) -> bool:
        return EnvironIO.env_path(env_name).exists()

    @staticmethod
    def try_build_config(env_config: dict, raise_on_fail: bool = False) -> Optional[list[dict]]:
        '''_summary_
        Attempts to build the base app config from the given env_config to test if it works

        Arguments:
            env_config {dict} 

        Keyword Arguments:
            raise_on_fail {bool} -- whether or not to raise an error if the config is invalid (default: False)
        Raises:
            e: validation error
        Returns:
            Optional[list[dict]] -- a list of dictionaries containing error information if the build fails
        '''
        try:
            BaseAppConfig(**env_config)
            return None
        except ValidationError as e:
            if raise_on_fail:
                raise e
            error_info = []
            for error in e.errors():
                error_info.append({
                    'field': error['loc'],
                    'reason': error['msg'],
                    'type': error['type']
                })
            return error_info

    @staticmethod
    def export_env(env_config: dict, env_name: str) -> None:
        '''_summary_
        Creates a new .env file in '.environment' with the <env_name>.env file name 
        the given env_config. 
        already exists.

        Arguments:
            env_config {dict} -- a dictionary representation of the AppConfig class
            env_name {str} -- the name of the env file 
        '''
        EnvironIO.ENV_DIR.mkdir(exist_ok=True)

        env_file = EnvironIO.env_path(env_name)
        EnvironIO.try_build_config(env_config, raise_on_fail=True)
        with env_file.open("w") as f:
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")

    @staticmethod
    def build_config(env_config: dict) -> BaseAppConfig:
        return BaseAppConfig(**env_config)


# -----------------------------------
# Example Usage (uncomment to test)
# -----------------------------------
#
# 1. Listing environ files
# print("Environ files:", EnvironIO.list_environs())
#
# 2. Export a new environment config
# new_config = {
#     "API_KEY": "1234567890",
#     "DEBUG": "True",
#     "DB_NAME": "my_database"
# }
# EnvironIO.export_env_config(new_config, "dev")
#
# 3. Load the new file
# loaded = EnvironIO.load_env("dev")
# print("Loaded Environ:", loaded)
#
# 4. Check updated environment list
# print("Environ files:", EnvironIO.list_environs())
