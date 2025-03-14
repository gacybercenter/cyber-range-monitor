from typing import Annotated
from enum import StrEnum

from fastapi import Path
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


class DatasouceType(StrEnum):
    OPENSTACK = "openstack"
    GUAC = "guacamole"
    SALT = "saltstack"
