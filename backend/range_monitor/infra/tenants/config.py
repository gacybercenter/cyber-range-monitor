import httpx
from pydantic import Field

from range_monitor.core.config_class import TomlSection


class HttpxLimits(TomlSection):
    '''config.toml -> [httpx.limits]'''
    max_keepalive_connections: int = 5
    max_connections: int = 50
    keepalive_expiry: int = 30  # seconds


class HttpxTimeouts(TomlSection):
    '''config.toml -> [httpx.timeout]'''
    # seconds
    connect: float = 5.0
    read: float = 10.0
    write: float = 10.0
    pool: float = 5.0

class HttpxConfig(TomlSection):
    '''config.toml -> [httpx]'''
    max_redirects: int = 5
    limits: HttpxLimits = Field(default_factory=HttpxLimits)
    timeout: HttpxTimeouts = Field(default_factory=HttpxTimeouts)
    http2: bool = True

    @property
    def client_kwargs(self) -> dict:
        return {
            'limits': httpx.Limits(
                max_keepalive_connections=self.limits.max_keepalive_connections,
                max_connections=self.limits.max_connections,
                keepalive_expiry=self.limits.keepalive_expiry,
            ),
            'timeout': httpx.Timeout(
                connect=self.timeout.connect,
                read=self.timeout.read,
                write=self.timeout.write,
                pool=self.timeout.pool,
            ),
            'max_redirects': self.max_redirects,
            'http2': self.http2,
        }

