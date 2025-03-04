from enum import StrEnum
from typing import Union


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "read_only"

    @classmethod
    def get_role_level(cls, role: "Role") -> int:
        hierarchy = {cls.ADMIN: 3, cls.USER: 2, cls.READ_ONLY: 1}
        return hierarchy.get(role, -1)

    def __lt__(self, other: "Role") -> bool:
        return self.get_role_level(self) < self.get_role_level(other)

    def __le__(self, other: "Role") -> bool:
        return self.get_role_level(self) <= self.get_role_level(other)

    def __ge__(self, other: "Role") -> bool:
        return self.get_role_level(self) >= self.get_role_level(other)


class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __lt__(self, other: Union["LogLevel", str]) -> bool:
        if isinstance(other, str):
            other = LogLevel(other)

        hierarchy = {self.INFO: 1, self.WARNING: 2, self.ERROR: 3, self.CRITICAL: 4}
        return hierarchy.get(self, -1) < hierarchy.get(other, -1)
