
import redis.asyncio as aioredis


class RedisRepo:
    """
    Represents a redis repository, the namespace is used as a
    prefix for all keys and is a class attribute.

    When using this, remember to always encode and decode values
    before setting or getting them from redis.
    """

    namespace: str

    def __init__(self, client: aioredis.Redis) -> None:
        self.client: aioredis.Redis = client

    def key(self, *parts: str) -> str:
        """
        Constructs a namespaced redis key by joining the namespace

        Returns
        -------
        str
        """
        return ':'.join([self.namespace, *(part for part in parts if part)])