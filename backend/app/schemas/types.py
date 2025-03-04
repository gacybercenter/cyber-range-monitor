from typing import Annotated

from fastapi import Path
from pydantic import PositiveInt, StringConstraints

PathID = Annotated[int, Path(..., description="The id of model to act on.", gt=0)]


PositiveNumber = Annotated[int, PositiveInt]
FixedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
