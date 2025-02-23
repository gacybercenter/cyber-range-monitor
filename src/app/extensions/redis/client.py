

import json
from typing import Optional
import redis

from app.security import crypto
from .constant import REDIS_CONFIG


class RedisClient:
    _instance: 'RedisClient' = None  # type: ignore
    _client: redis.Redis = None  # type: ignore

    def connect(self) -> None:
        self._client = redis.Redis(
            host=REDIS_CONFIG.HOST,
            port=REDIS_CONFIG.PORT,
            db=REDIS_CONFIG.DB,
            password=REDIS_CONFIG.PASSWORD,
            decode_responses=True
        )

    @classmethod    
    def get_instance(cls) -> 'RedisClient':
        if not cls._instance:
            cls._instance = cls()
            cls._instance.connect()
        return cls._instance

    def _santize_key(self, key: str) -> str:
        return key.replace(":", "_")

    def set_encrypted(self, key: str, data: dict, ex: Optional[int] = None) -> None:
        safe_key = self._santize_key(key)
        json_data = json.dumps(data)
        encrypted_data = crypto.encrypt_data(json_data)
        self._client.set(safe_key, encrypted_data, ex=ex)

    def get_decrypted(self, key: str) -> Optional[dict]:
        safe_key = self._santize_key(key)
        encrypted = self._client.get(safe_key)
        if not encrypted:
            return None
        try:
            decrypted = crypto.decrypt_data(encrypted)  # type: ignore
            return json.loads(decrypted)
        except Exception:
            return None

    def remove(self, key: str) -> None:
        safe_key = self._santize_key(key)
        if not self._client.exists(safe_key):
            return
        self._client.delete(safe_key)

    def set_key_expiration(self, key: str, ex: int) -> None:
        safe_key = self._santize_key(key)
        self._client.expire(safe_key, ex)



async def get_redis_client() -> RedisClient:
    return RedisClient.get_instance()