from typing import Callable, Awaitable, Literal
from typing import Annotated

from fastapi import Path, Request, Response
from pydantic import PositiveInt, StringConstraints

# Generic Utility Types

PathID = Annotated[int, Path(
    ...,
    description="The id of model.",
    gt=0
)]

AlphanumericStr = Annotated[str, StringConstraints(
    min_length=1,
    max_length=128,
    pattern=r"^\w+$"
)]

PositiveNumber = Annotated[int, PositiveInt]
FixedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]

type CallNext = Callable[[Request], Awaitable[Response]]
LogLevels = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG"
]