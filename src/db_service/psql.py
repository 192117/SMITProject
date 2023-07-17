from tortoise import Tortoise

from src.database import config


async def init_db():
    await Tortoise.init(
        db_url=f'postgres://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@'
               f'{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}',
        modules={
            'models': [
                'src.database.models',
            ],
        },
    )
    await Tortoise.generate_schemas()


async def get_db() -> Tortoise:
    await init_db()
    return Tortoise


async def close_db():
    await Tortoise.close_connections()
