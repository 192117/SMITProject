import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import rate
from src.core import config
from src.db import psql, redis

app = FastAPI(
    title='REST API для расчёта стоимости страхования',
    description='Сервис по расчёту стоимости страхования в зависимости от типа груза и объявленной стоимости (ОС).',
    version='1.0.0',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup_event():
    psql.tortoise = await psql.get_db()
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


@app.on_event('shutdown')
async def shutdown_event():
    await redis.redis.close()
    await psql.tortoise.close_connections()


app.include_router(rate.router, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
