import redis.asyncio
from app.core.config import settings


redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.asyncio.from_url(redis_url, decode_responses=True)
