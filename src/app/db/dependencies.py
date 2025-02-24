from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .core import get_db

DatabaseRequired = Annotated[AsyncSession, Depends(get_db)]