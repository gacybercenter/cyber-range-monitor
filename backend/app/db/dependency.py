from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from .main import get_session


DatabaseDep = Annotated[AsyncSession, Depends(get_session)]
