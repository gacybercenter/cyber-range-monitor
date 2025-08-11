from collections.abc import Awaitable, Callable
from typing import Annotated, Literal, TypeAlias

from fastapi import Path, Request, Response
from pydantic import PositiveInt, StringConstraints

# Generic Utility Types

PathID = Annotated[int, Path(..., description="The id of model.", gt=0)]

AlphanumericStr = Annotated[
    str, StringConstraints(min_length=1, max_length=128, pattern=r"^\w+$")
]

PositiveNumber = Annotated[int, PositiveInt]
FixedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]

CallNext: TypeAlias = Callable[[Request], Awaitable[Response]]

LevelNames = Literal["TRACE", "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

LevelNumber = Literal[0, 10, 20, 30, 40, 50]
