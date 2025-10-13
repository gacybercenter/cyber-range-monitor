
# import hashlib

# import msgspec
# from redis.asyncio import Redis

# from range_monitor.guac.schema import Topology


# def topology_cache_key() -> str:
#     return 'guac:topology:cache'


# async def cache_topology(
#     redis: Redis,
#     topology: Topology,
#     hash: str
# ) -> None:

#     encoded = msgspec.json.encode(topology)

#     pipe = redis.pipeline()

#     redis.hset(
#         topology_cache_key(),
#         mapping={
#             'dump': encoded,
#             'hash': hash,
#         },
#     )
#     pipe.expire(topology_cache_key(), 300)  # 5 minutes

#     await pipe.execute()

# # NOT DONE
# class TopologyCache:

#     def __init__(self, redis: Redis) -> None:
#         self.redis = redis

#     @staticmethod
#     def create_hash(raw_topology: dict, active_only: bool) -> str:
#         raw_topology['activeOnly'] = active_only
#         encoded = msgspec.json.encode(raw_topology, order='sorted')
#         return hashlib.sha256(encoded).hexdigest()

#     async def get_cached(self, active_only: bool) -> tuple[Topology | None, str | None]:

#         data = await self.redis.hgetall(topology_cache_key())  # type: ignore

#         if not data or 'dump' not in data or 'hash' not in data:
#             return None, None

#         try:
#             topology = msgspec.json.decode(data['dump'])
#         except msgspec.ValidationError:
#             return None, None

#         return topology, data['hash']

#     async def hash_matches_cache(self, hash: str) -> bool:

#         data = await self.redis.hget(topology_cache_key(), 'hash') # type: ignore
#         if not data:
#             return False
#         return data == hash

#     async def cache(
#         self,
#         hash: str,
#         topology: Topology,
#         *,
#         ttl: int = 300
#     ) -> str:
#         pipe = self.redis.pipeline()
#         dumped = topology.dump()

#         pipe.hset(
#             topology_cache_key(),
#             mapping={
#                 'dump': msgspec.json.encode(dumped),
#                 'hash': hash,
#             },
#         )
#         pipe.expire(topology_cache_key(), ttl)
#         await pipe.execute()
#         return hash
