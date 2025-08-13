from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure import db, redis

DatabaseDepends = Depends(db.get_session)
DatabaseDep = Annotated[AsyncSession, DatabaseDepends]

RedisDepends = Depends(redis.get_redis_client)
RedisDep = Annotated[aioredis.Redis, RedisDepends]
