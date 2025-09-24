

from typing import Any, Literal

from range_monitor.core.config_class import TomlSection


class SqliteConfig(TomlSection):
    '''config.toml -> [sqlite.options]'''
    echo: bool = False
    timeout: int = 30
    autoflush: bool = True
    expire_on_commit: bool = False
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    pool_size: int = 5
    max_overflow: int = 10
    future: Literal[True] = True
    pragmas: list[str] = []

    @property
    def engine_kwargs(self) -> dict[str, Any]:
        return {
            'echo': self.echo,
            'pool_pre_ping': self.pool_pre_ping,
            'pool_recycle': self.pool_recycle,
            'future': self.future,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'connect_args': {
                'check_same_thread': False,
                'timeout': self.timeout,
            }
        }
