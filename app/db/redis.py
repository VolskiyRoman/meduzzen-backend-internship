import asyncio
import aioredis
from app.core.config import settings


async def main():
    redis = await aioredis.create_redis_pool(
        (settings.REDIS_HOST, settings.REDIS_PORT),
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB
    )

    await redis.set("key", "value")
    result = await redis.get("key")
    print(f"Значення з Redis: {result.decode()}")

    redis.close()
    await redis.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
