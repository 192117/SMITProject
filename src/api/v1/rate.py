from http import HTTPStatus
from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.rate import CostService, RateService, get_cost_service, load_data_service

router = APIRouter()


class Rate(BaseModel):
    """Represents a rate for calculating insurance costs based on cargo type and declared value (OS) for
    response to user."""
    date: str
    cargo_type: str
    rate: Union[int, float]


class Cost(BaseModel):
    """Represents the insurance cost for a given cargo type for response to user."""
    cost: Union[int, float]
    cargo_type: str


@router.post('/load_rate',
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
    """Load rates for calculating insurance costs based on cargo type and declared value (OS).

    :param data: The input data containing rates for different cargo types.
    :param loading_rate: The RateService instance used for loading the rates.
    :return: A list of Rate objects representing the loaded rates.
    """
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
    """Get the insurance cost based on declared value (OS), cargo type, and date.

    :param value: The declared value (OS) for insurance calculation.
    :param cargo_type: The type of cargo for which the insurance cost is calculated.
    :param date: The date for which the insurance cost is applicable.
    :param get_cost: The CostService instance used for calculating the insurance cost.
    :return: A Cost object representing the calculated insurance cost
    """
    cost = await get_cost.get_cost(value, cargo_type, date)
    if not cost:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Rate not found')
    return Cost(cost=cost[0], cargo_type=cost[1])
