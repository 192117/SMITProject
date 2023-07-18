from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

import orjson
import tortoise
from fastapi import Depends
from redis.asyncio import Redis
from tortoise import Tortoise

from src.db.psql import get_tortoise
from src.db.redis import get_redis
from src.models.models import Rate, RatePydantic

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 2


class RateService:
    def __init__(self, tortoise: Tortoise):
        self.tortoise = tortoise

    async def load_rate(self, data: Dict[str, List[Dict[str, Union[str, float]]]]) -> List[RatePydantic]:
        for date, values in data.items():
            for value in values:
                try:
                    await Rate.create(date=date, cargo=value['cargo_type'], value=value['rate'])
                except tortoise.exceptions.IntegrityError:
                    pass
        return await RatePydantic.from_queryset(Rate.all())


class CostService:
    def __init__(self, redis: Redis, tortoise: Tortoise):
        self.redis = redis
        self.tortoise = tortoise

    async def get_cost(self, value: Union[int, float], cargo_type: str, date: str) \
            -> Optional[Tuple[Union[int, float], str]]:
        cost = await self._get_cost_from_cache(value, cargo_type, date)
        if not cost:
            cost = await self._count_cost(value, cargo_type, date)
            if not cost:
                return None
            await self._put_cost_to_cache(cost, value, cargo_type, date)
        return (cost, cargo_type)

    async def _count_cost(self, value: Union[int, float], cargo_type: str, date: str) -> Optional[Union[int, float]]:
        try:
            answer = await RatePydantic.from_queryset_single(Rate.get(date=date, cargo=cargo_type))
            result = answer.value * value
            response = round(result, 2)
        except tortoise.exceptions.DoesNotExist:
            return None
        return response

    async def _get_cost_from_cache(self, value: Union[int, float], cargo_type: str, date: str) \
            -> Optional[Union[int, float]]:
        data = await self.redis.get(f'{value}-{cargo_type}-{date}')
        if not data:
            return None
        return orjson.loads(data)

    async def _put_cost_to_cache(self, cost: Union[int, float], value: Union[int, float], cargo_type: str, date: str):
        await self.redis.set(f'{value}-{cargo_type}-{date}', cost, FILM_CACHE_EXPIRE_IN_SECONDS)


def load_data_service(
        tortoise: Tortoise = Depends(get_tortoise),
) -> RateService:
    return RateService(tortoise)


@lru_cache()
def get_cost_service(
        redis: Redis = Depends(get_redis),
        tortoise: Tortoise = Depends(get_tortoise),
) -> CostService:
    return CostService(redis, tortoise)
