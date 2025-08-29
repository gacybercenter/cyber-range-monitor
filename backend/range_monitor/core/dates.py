from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, PlainSerializer


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def stringify_dt(dt: datetime) -> str:
    return dt.isoformat().replace('+00:00', 'Z')


UTCDate = Annotated[
    AwareDatetime,
    AfterValidator(_to_utc),
    PlainSerializer(stringify_dt, return_type=str),
]

def utcnow() -> datetime:
    return datetime.now(tz=UTC)

