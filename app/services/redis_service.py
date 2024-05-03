from app.core.config import settings
from app.db.redis_connection import redis_connection


class RedisService:
    def __init__(self):
        self.port = settings.REDIS_PORT
        self.host = settings.REDIS_HOST
        self.connection = redis_connection

    async def connect(self, key, serialized_result, expiration):
        await self.connection.set(key, serialized_result, expiration)


redis_service = RedisService()
