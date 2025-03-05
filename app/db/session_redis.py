from redis.asyncio import Redis

from app.config.settings import settings


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


async def set_redis_value(key: str, value: str):
    await redis_client.set(key, value)


async def get_redis_value(key: str):
    return await redis_client.get(key)
