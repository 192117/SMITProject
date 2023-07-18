from typing import Optional

from tortoise import Tortoise

from src.core import config

tortoise: Optional[Tortoise] = None

async def init_db():
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
    await init_db()
    return Tortoise


async def get_tortoise() -> Tortoise:
    return tortoise

# {
#     "2022-03-02": [
#         {
#             "cargo_type": "Glass",
#             'rate': 0.2223,
#         },
#         {
#             "cargo_type": "Other",
#             "rate": 0.7562,
#         }
#     ],
#     "2022-03-01": [
#         {
#             "cargo_type": "Glass",
#             'rate': 0.123,
#         },
#         {
#             "cargo_type": "Other",
#             "rate": 0.562,
#         }
#     ],
# }