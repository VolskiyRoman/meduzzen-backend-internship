from app.core.config import settings
from app.db.redis_connection import redis_connection


class RedisService:
    def __init__(self):
        self.port = settings.REDIS_PORT
        self.host = settings.REDIS_HOST
        self.connection = redis_connection

    async def redis_set(self, key, serialized_result, expiration):
        await self.connection.set(key, serialized_result, expiration)

    async def redis_get(self, key):
        result = await self.connection.get(key)
        return result or None


redis_service = RedisService()
