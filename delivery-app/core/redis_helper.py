from redis.asyncio import Redis
import json

from typing import Optional


class RedisHelper:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)

    async def set(self, key: str, value: dict, expire: int = 3600):
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def get(self, key: str) -> Optional[dict]:
        result = await self.redis.get(key)
        return json.loads(result) if result else None

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def close(self):
        await self.redis.close()
