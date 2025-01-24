from api.config.builds import Settings
from typing import Optional

settings: Settings = Settings()  # type: ignore


def set_settings(config: Optional[Settings] = None) -> None:
    if not config:
        return
    global settings
    settings = config
