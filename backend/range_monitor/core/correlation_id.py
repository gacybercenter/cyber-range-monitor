import uuid
from contextvars import ContextVar, Token

_correlation_id: ContextVar[str] = ContextVar(
    'correlation_id',
    default='not-set'
)


def generate() -> str:
    return uuid.uuid4().hex

def set_id(val: str | None) -> Token[str]:
    cid = val or generate()
    return _correlation_id.set(cid)


def get_id() -> str:
    return _correlation_id.get()


def reset(token: Token[str]) -> None:
    _correlation_id.reset(token)