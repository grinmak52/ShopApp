import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from database.core.config import settings

log = logging.getLogger(__name__)

redis_client = Redis.from_url(settings.redis.url, decode_responses=True)


class Cache:
    def __init__(self, client: Redis, ttl: int):
        self.client = client
        self.ttl = ttl

    async def get(self, key: str) -> str | None:
        try:
            return await self.client.get(key)
        except RedisError:
            log.warning("Redis get failed: %s", key)
            return None

    async def set(self, key: str, value: str) -> None:
        try:
            await self.client.set(key, value, ex=self.ttl)
        except RedisError:
            log.warning("Redis set failed: %s", key)

    async def delete(self, *keys: str) -> None:
        try:
            await self.client.delete(*keys)
        except RedisError:
            log.warning("Redis delete failed: %s", keys)

    async def version(self, key: str) -> int:
        try:
            return int(await self.client.get(key) or 0)
        except RedisError:
            return 0

    async def bump(self, key: str) -> None:
        try:
            await self.client.incr(key)
        except RedisError:
            log.warning("Redis incr failed: %s", key)


cache = Cache(redis_client, settings.redis.ttl_seconds)