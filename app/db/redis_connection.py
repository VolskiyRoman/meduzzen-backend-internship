import redis.asyncio as redis
from app.core.config import settings


redis_connection = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True)
