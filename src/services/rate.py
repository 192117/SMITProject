from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

import orjson
import tortoise
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from tortoise import Tortoise

from src.db.psql import get_tortoise
from src.db.redis import get_redis
from src.models.models import Rate, RatePydantic

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 2


class RateService:
    """Service class for loading and retrieving rate data for calculating insurance costs."""
    def __init__(self, tortoise: Tortoise):
        self.tortoise = tortoise

    async def load_rate(self, data: Dict[str, List[Dict[str, Union[str, float]]]]) -> List[RatePydantic]:
        """Load rate data for calculating insurance costs based on cargo type and declared value (OS).

        :param data: Input data containing rates for different cargo types.
        :return: A list of RatePydantic objects representing the loaded rates.
        """
        for date, values in data.items():
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400,
                                    detail=f'Invalid date format for key <{date}>. Must be in <YYYY-MM-DD> format.')
            for value in values:
                try:
                    await Rate.create(date=date, cargo=value['cargo_type'], value=value['rate'])
                except tortoise.exceptions.IntegrityError:
                    pass
        return await RatePydantic.from_queryset(Rate.filter(created__lte=datetime.now() - timedelta(minutes=5)))


class CostService:
    """Service class for calculating insurance costs and caching results."""
    def __init__(self, redis: Redis, tortoise: Tortoise):
        self.redis = redis
        self.tortoise = tortoise

    async def get_cost(self, value: Union[int, float], cargo_type: str, date: str) \
            -> Optional[Tuple[Union[int, float], str]]:
        """Get the insurance cost based on declared value (OS), cargo type, and date.

        :param value: The declared value (OS) for insurance calculation.
        :param cargo_type: The type of cargo for which the insurance cost is calculated.
        :param date: The date for which the insurance cost is applicable.
        :return: A tuple containing the calculated insurance cost and cargo type, or None if the rate data is not found.
        """
        cost = await self._get_cost_from_cache(value, cargo_type, date)
        if not cost:
            cost = await self._count_cost(value, cargo_type, date)
            if not cost:
                return None
            await self._put_cost_to_cache(cost, value, cargo_type, date)
        return (cost, cargo_type)

    async def _count_cost(self, value: Union[int, float], cargo_type: str, date: str) -> Optional[Union[int, float]]:
        """Calculate the insurance cost based on the declared value (OS), cargo type, and date.

        :param value: The declared value (OS) for insurance calculation.
        :param cargo_type: The type of cargo for which the insurance cost is calculated.
        :param date: The date for which the insurance cost is applicable.
        :return: The calculated insurance cost, or None if the rate data is not found.
        """
        try:
            answer = await RatePydantic.from_queryset_single(Rate.get(date=date, cargo=cargo_type))
            result = answer.value * value
            response = round(result, 2)
        except tortoise.exceptions.DoesNotExist:
            return None
        return response

    async def _get_cost_from_cache(self, value: Union[int, float], cargo_type: str, date: str) \
            -> Optional[Union[int, float]]:
        """Retrieve the insurance cost from the cache.

        :param value: The declared value (OS) for insurance calculation.
        :param cargo_type: The type of cargo for which the insurance cost is calculated.
        :param date: The date for which the insurance cost is applicable.
        :return: The cached insurance cost, or None if the data is not found in the cache.
        """
        data = await self.redis.get(f'{value}-{cargo_type}-{date}')
        if not data:
            return None
        return orjson.loads(data)

    async def _put_cost_to_cache(self, cost: Union[int, float], value: Union[int, float], cargo_type: str, date: str):
        """Cache the insurance cost.

        :param cost: The calculated insurance cost to be cached.
        :param value: The declared value (OS) for insurance calculation.
        :param cargo_type: The type of cargo for which the insurance cost is calculated.
        :param date: The date for which the insurance cost is applicable.
        """
        await self.redis.set(f'{value}-{cargo_type}-{date}', cost, FILM_CACHE_EXPIRE_IN_SECONDS)


def load_data_service(
        tortoise: Tortoise = Depends(get_tortoise),
) -> RateService:
    """Dependency function to create a RateService instance for loading rate data.

    :param tortoise: The Tortoise database connection instance.
    :return: A RateService instance for loading rate data.
    """
    return RateService(tortoise)


@lru_cache()
def get_cost_service(
        redis: Redis = Depends(get_redis),
        tortoise: Tortoise = Depends(get_tortoise),
) -> CostService:
    """Dependency function to create a CostService instance for calculating insurance costs.

    :param redis: The Redis client instance used for caching.
    :param tortoise: The Tortoise database connection instance.
    :return: A CostService instance for calculating insurance costs.
    """
    return CostService(redis, tortoise)
