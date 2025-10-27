'''
Context variables for tracking request-specific data.
'''
import uuid
from contextvars import ContextVar
from typing import Literal

correlation_id: ContextVar[str | None] = ContextVar(
    'correlation_id',
    default=None
)

ActorTypes = Literal['api', 'worker', 'migrator']

actor: ContextVar[str | None] = ContextVar(
    'actor',
    default=None
)

task_id: ContextVar[str | None] = ContextVar(
    'task_id',
    default=None
)


def generate_id(length: int = 32) -> str:
    '''
    Generates a unique identifier string.

    Returns
    -------
    str
    '''
    base = uuid.uuid4().hex
    if length >= 32:
        return base
    return base[:length]
