from typing import Annotated

from fastapi import Path

PathIdInt = Annotated[int, Path(..., description="The id of model.", gt=0)]
