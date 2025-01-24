from multiprocessing import Value
from api.config.builds import BaseConfig
from typing import Any
from pathlib import Path
import secrets as s
import random


ENVIRONMENTS = Path('.environemnt')
RUNNING_CONFIG = Path('.env')


# WIP

def set_preset() -> tuple[dict, dict]:
    documentation = {}
    preset = {}
    for fkey in BaseConfig.model_fields.keys():
        current_field = BaseConfig.model_fields[fkey]
        if current_field.is_required():
            preset[fkey] = None
        else:
            preset[fkey] = current_field.default
        documentation[fkey] = current_field.description
    return preset, documentation


class ConfigBuilder:

    def __init__(self) -> None:
        preset, documentation = set_preset()
        self.preset = preset
        self.documentation = documentation

    def settings_like(self, phrase: str) -> list[str]:
        matches = []
        for field in self.documentation.keys():
            if phrase.lower() in field.lower():
                matches.append(field)
        return matches

    def inspect(self) -> dict:
        return self.preset

    def describe(self, field_name: str) -> str:
        if not field_name in self.documentation.keys():
            matches = self.settings_like(field_name)
            if not matches:
                return 'No settings found for: ' + field_name

            return 'Did you mean: ' + ', '.join(matches)

        return self.documentation[field_name]

    def try_resolve(self, field_name: str) -> Any:
        matches = self.settings_like(field_name)
        if not matches:
            return 'No settings found for: ' + field_name

        return 'Did you mean: ' + ', '.join(matches)

    def set_field(self, field_name: str, value: Any) -> tuple[bool, Any]:
        if not field_name in self.documentation.keys():
            return (False, self.try_resolve(field_name))

        self.preset[field_name] = value
        return (True, value)

    def export_config(self, env_name: str) -> bool:

        unset_required_fields = []
        for field in self.preset.keys():
            if self.preset[field] is None:
                unset_required_fields.append(field)

        if unset_required_fields:
            required = ', '.join(unset_required_fields)
            raise ValueError(f"Required fields are not set: {required}")

        export_path = Path('env', f'.{env_name}.env')
        if not env_name:
            export_path = RUNNING_CONFIG
        with export_path.open('w') as f:
            for field in self.preset.keys():
                f.write(f'{field}={self.preset[field]}\n')
        return True

    def set_secret_keys(self) -> bool:
        secrets = self.settings_like('secret')
        secret_len = random.randint(20, 32)
        try:
            for secret in secrets:
                self.preset[secret] = s.token_hex(secret_len)
            return True
        except Exception as e:
            return False

    def disable_documentation(self) -> bool:
        self.preset['DOCS_URL'] = None
        self.preset['OPENAPI_URL'] = None
        self.preset['REDOC_URL'] = None
        return True

    def set_db_url(self, db_url: str) -> None:
        if not db_url.endswith('.db'):
            raise ValueError('Database URL must end with .db')

        url_prefix = 'sqlite+aiosqlite:///'
        self.preset['DATABASE_URL'] = url_prefix + db_url

    def disable_logging(self) -> None:
        self.preset['CONSOLE_LOG'] = False
        self.preset['WRITE_LOGS'] = False

    def __setitem__(self, key: str, value: Any) -> None:
        self.set_field(key, value)


# placeholder for now
def initialize_dev_settings() -> None:
    config_builder = ConfigBuilder()
    config_builder.set_secret_keys()
    config_builder['DEBUG'] = True
    config_builder['DATABASE_ECHO'] = True
    config_builder['REDIS_PORT'] = 6379
    config_builder['REDIS_DB'] = 0
    
    config_builder.set_db_url('./instance/app.db')
    
    
    
    config_builder.export_config('')
