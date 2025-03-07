from enum import StrEnum

from typing import Union


class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __lt__(self, other: Union['LogLevel', str]) -> bool:
        if isinstance(other, str):
            other = LogLevel(other)

        hierarchy = {self.INFO: 1, self.WARNING: 2,
                     self.ERROR: 3, self.CRITICAL: 4}
        return hierarchy.get(self, -1) < hierarchy.get(other, -1)
