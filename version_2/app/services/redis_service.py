import json
from typing import Optional
import redis

from app.core.security import crypto_utils
from app.config import running_config


settings = running_config()


class RedisClient:
    _instance: 'RedisClient' = None  # type: ignore
    _client: redis.Redis = None  # type: ignore

    @classmethod
    def get_instance(cls) -> 'RedisClient':
        if cls._instance is None:
            cls._instance = cls()
            cls._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        return cls._instance

    def _santize_key(self, key: str) -> str:
        return key.replace(":", "_")

    def set_encrypted(self, key: str, data: dict, ex: Optional[int] = None) -> None:
        safe_key = self._santize_key(key)
        json_data = json.dumps(data)
        encrypted_data = crypto_utils.encrypt_data(json_data)
        self._client.set(safe_key, encrypted_data, ex=ex)

    def get_decrypted(self, key: str) -> Optional[dict]:
        safe_key = self._santize_key(key)
        encrypted = self._client.get(safe_key)
        if not encrypted:
            return None
        try:
            decrypted = crypto_utils.decrypt_data(encrypted)  # type: ignore
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
