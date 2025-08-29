"""
utils for session management, these seem trivial but are easier
to mock and test here than in the repo or bearer
"""
from datetime import UTC, datetime, timedelta

from range_monitor.users.sessions import constant


def utcnow() -> datetime:
    return datetime.now(tz=UTC)

def calc_max_age(created_at: datetime) -> timedelta:
    elapsed = utcnow() - created_at
    return constant.SESSION_MAX_AGE - elapsed

def calc_idle_timeout_remaing(last_seen: datetime) -> timedelta:
    elapsed = utcnow() - last_seen
    return constant.SESSION_IDLE_TIMEOUT - elapsed

def idle_timeout_at(last_seen: datetime) -> datetime:
    return last_seen + constant.SESSION_IDLE_TIMEOUT

def max_age_at(created_at: datetime) -> datetime:
    return created_at + constant.SESSION_MAX_AGE

def has_reached_max_age(created_at: datetime) -> bool:
    return calc_max_age(created_at) <= timedelta(0)

def has_reached_idle_timeout(last_seen: datetime) -> bool:
    return calc_idle_timeout_remaing(last_seen) <= timedelta(0)

def idle_timeout_seconds() -> int:
    return int(constant.SESSION_IDLE_TIMEOUT.total_seconds())


def max_age_seconds() -> int:
    return int(constant.SESSION_MAX_AGE.total_seconds())