from typing import Dict, List, Optional, Union

import tortoise
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse

from src.database import models
from src.db_service.psql import close_db, get_db

app = FastAPI(
    title='REST API для расчёта стоимости страхования',
    description='Сервис по расчёту стоимости страхования в зависимости от типа груза и объявленной стоимости (ОС).',
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup_event():
    await get_db()


@app.on_event('shutdown')
async def shutdown_event():
    await close_db()


@app.post('/load_rate', response_model=List[models.RatePydantic])
async def load_rate(data: Dict[str, List[Dict[str, Union[str, float]]]]):
    for date, values in data.items():
        for value in values:
            await models.Rate.create(date=date, cargo=value['cargo_type'], value=value['rate'])
    return await models.RatePydantic.from_queryset(models.Rate.all())


@app.get('/get_cost', response_model=Optional[Dict[str, Union[float, int]]])
async def get_cost(value: Union[int, float], cargo_type: str, date: str):
    try:
        answer = await models.RatePydantic.from_queryset_single(models.Rate.get(date=date, cargo=cargo_type))
        result = answer.value * value
        response = {answer.cargo: round(result,2)}
        return response
    except tortoise.exceptions.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Requested data not found')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
