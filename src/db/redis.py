from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """ Get the current Redis client instance.

    :return: The current Redis client instance, or None if it hasn't been initialized.
    """
    return redis
