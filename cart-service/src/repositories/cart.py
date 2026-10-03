import uuid

from redis.asyncio import Redis


class CartRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _key(user_id: uuid.UUID) -> str:
        return f"cart:{user_id}"

    async def get_all(self, user_id: uuid.UUID) -> dict[str, int]:
        data = await self.redis.hgetall(self._key(user_id))
        return {product_id: int(qty) for product_id, qty in data.items()}

    async def count(self, user_id: uuid.UUID) -> int:
        return await self.redis.hlen(self._key(user_id))

    async def exists(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        return bool(await self.redis.hexists(self._key(user_id), str(product_id)))

    async def increment(self, user_id: uuid.UUID, product_id: uuid.UUID, qty: int) -> int:
        return await self.redis.hincrby(self._key(user_id), str(product_id), qty)

    async def set_quantity(self, user_id: uuid.UUID, product_id: uuid.UUID, qty: int) -> None:
        await self.redis.hset(self._key(user_id), str(product_id), qty)

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> int:
        return await self.redis.hdel(self._key(user_id), str(product_id))

    async def clear(self, user_id: uuid.UUID) -> None:
        await self.redis.delete(self._key(user_id))