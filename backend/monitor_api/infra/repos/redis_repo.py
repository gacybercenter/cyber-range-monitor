from typing import Any, Literal, TypeVar

import msgspec
import redis.asyncio as aioredis

S = TypeVar('S', bound=msgspec.Struct)


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

    def encode(
        self, v: Any, *, order: Literal[None, 'deterministic', 'sorted'] = None
    ) -> bytes:
        """
        Encodes a value to bytes using msgspec.

        Parameters
        ----------
        v : Any

        Returns
        -------
        bytes
        """
        return msgspec.msgpack.encode(v, order=order)

    def decode(self, b: bytes, *, struct: type[S]) -> S:
        """
        Decodes bytes to a value using msgspec.

        Parameters
        ----------
        b : bytes

        Returns
        -------
        Any
        """
        return msgspec.msgpack.decode(b, type=struct)
