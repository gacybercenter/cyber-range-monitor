from typing import Literal

from range_monitor.core.config_class import TomlSection

LoguruLevels = Literal[
    'TRACE',
    'DEBUG',
    'INFO',
    'SUCCESS',
    'WARNING',
    'ERROR',
    'CRITICAL',
]

LoguruCompression = Literal['zip', 'tar', 'gz', 'bz2', 'xz', 'none']

class LoggerConfig(TomlSection):
    '''config.toml -> [logger]'''
    format: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        'cid=<cyan>{extra[correlation_id]}</cyan> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
        '<level>{message}</level>'
    )
    level: LoguruLevels = 'INFO'
    mute: list[str] = []
    retention_days: int = 7
    rotation_mb: int = 100
    compression: LoguruCompression = 'zip'
    security_level_no: int = 25  # info is 20, warning is 30, so between these
    structured_logs: bool = True


    @property
    def stripped_format(self) -> str:
        return self.format.strip().strip('\n')
