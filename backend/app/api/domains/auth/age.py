from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from .settings import auth_settings
import time


def utcnow() -> int:
    return int(time.time())


class LifetimeType(StrEnum):
    IDLE = 'idle'
    MAX_AGE = 'max_age'
    REMEMBER_ME = 'remember_me'


SessionLifetimes = MappingProxyType(
    {
        LifetimeType.IDLE: auth_settings.idle_timeout,
        LifetimeType.MAX_AGE: auth_settings.base_max_age,
        LifetimeType.REMEMBER_ME: auth_settings.remember_me_max_age,
    }
)


@dataclass(slots=True)
class Timestamp:
    time: int = field(default_factory=utcnow)

    @property
    def date(self) -> datetime:
        return datetime.fromtimestamp(self.time, tz=UTC)


@dataclass(slots=True)
class SessionAge:
    remember_me: bool = False
    created_time: int = field(default_factory=utcnow)

    def timestamp(self, lifetime: LifetimeType) -> Timestamp:
        return Timestamp(self.calc_timestamp(lifetime))

    def calc_timestamp(self, lifetime: LifetimeType) -> int:
        if lifetime not in SessionLifetimes:
            raise ValueError(f'Invalid lifetime type: {lifetime}')
        return self.created_time + SessionLifetimes[lifetime]

    @property
    def created_at(self) -> Timestamp:
        return Timestamp(self.created_time)

    @property
    def idle_timeout(self) -> Timestamp:
        return self.timestamp(LifetimeType.IDLE)

    @property
    def max_age(self) -> Timestamp:
        if self.remember_me:
            return self.timestamp(LifetimeType.REMEMBER_ME)
        return self.timestamp(LifetimeType.MAX_AGE)

    @property
    def elapsed(self) -> int:
        return utcnow() - self.created_time

    @property
    def remaining(self) -> int:
        return self.max_age.time - self.elapsed

    def has_expired(self) -> bool:
        return self.remaining <= 0
