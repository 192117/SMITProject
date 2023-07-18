from typing import Optional

from tortoise import Tortoise

from src.core import config

tortoise: Optional[Tortoise] = None


async def init_db() -> None:
    """Initialize the database connection using Tortoise.

    Connects to the PostgreSQL database based on the configuration settings provided.
    This function should be called before performing any database operations.

    :return: None
    """
    await Tortoise.init(
        db_url=f'postgres://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@'
               f'{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}',
        modules={
            'models': [
                'src.models.models',
            ],
        },
    )
    await Tortoise.generate_schemas()


async def get_db() -> Tortoise:
    """Get the initialized Tortoise database instance.

    Calls `init_db()` to ensure the database is initialized before returning the Tortoise instance.

    :return: The initialized Tortoise database instance.
    """
    await init_db()
    return Tortoise


async def get_tortoise() -> Tortoise:
    """Get the current Tortoise database instance.

    :return: The current Tortoise database instance, or None if it hasn't been initialized.
    """
    return tortoise
