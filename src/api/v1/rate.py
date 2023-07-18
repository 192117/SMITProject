from http import HTTPStatus
from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.rate import CostService, RateService, get_cost_service, load_data_service

router = APIRouter()


class Rate(BaseModel):
    date: str
    cargo_type: str
    rate: Union[int, float]


class Cost(BaseModel):
    cost: Union[int, float]
    cargo_type: str


@router.get('/load_rate',
            response_model=List[Rate],
            summary='Загрузка тарифа',
            description='Загрузка тарифа для расчёту стоимости страхования в зависимости от типа груза и объявленной '
                        'стоимости (ОС)',
            response_description='Список тарифов',
            tags=['Тариф'],
            )
async def load_rate(
        data: Dict[str, List[Dict[str, Union[str, float]]]],
        loading_rate: RateService = Depends(load_data_service)) -> List[Rate]:
    rates = await loading_rate.load_rate(data)
    return [Rate(date=str(rate.date), cargo_type=rate.cargo, rate=rate.value) for rate in rates]


@router.get('/get_cost',
            response_model=Cost,
            summary='Получение стоимости страхования',
            description='Получение стоимости страхования в зависимости от ОС, типа груза и даты',
            response_description='Стоимость страхования',
            tags=['Страхование'],
            )
async def get_cost(
        value: Union[int, float],
        cargo_type: str,
        date: str,
        get_cost: CostService = Depends(get_cost_service)) -> Cost:
    cost = await get_cost.get_cost(value, cargo_type, date)
    if not cost:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Rate not found')
    return Cost(cost=cost[0], cargo_type=cost[1])
