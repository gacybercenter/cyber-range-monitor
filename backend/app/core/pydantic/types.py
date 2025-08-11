from typing import Annotated

from pydantic import PositiveInt, StringConstraints

# Generic Utility Types


AlphaString = Annotated[
    str, StringConstraints(min_length=1, max_length=128, pattern=r"^\w+$")
]

PositiveNumber = Annotated[int, PositiveInt]
FixedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
