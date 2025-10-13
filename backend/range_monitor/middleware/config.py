from range_monitor.core.config_class import TomlSection


class CorsConfig(TomlSection):
    """config.toml -> [cors]"""

    allow_origins: list[str] = ['*']
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']
    allow_credentials: bool = True
