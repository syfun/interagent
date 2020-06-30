from typing import Optional

import aioredis

from app.settings import REDIS_URL

ENCODING = 'utf-8'


class Redis:
    redis: Optional[aioredis.Redis] = None

    def __init__(self, address: str):
        self.address: str = address

    async def connect(self):
        self.redis = await aioredis.create_redis_pool(self.address)

    async def disconnect(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def execute(self, command, *args, **kwargs):
        return await self.redis.execute(command, *args, **kwargs, encoding=ENCODING)

    def __getattr__(self, item):
        return getattr(self.redis, item)


redis = Redis(REDIS_URL)
