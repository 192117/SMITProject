from pydantic import BaseSettings


class Settings(BaseSettings):
    """The settings class that the pydantic uses to work with environment variables."""

    POSTGRES_DB: str = ''
    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''
    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: int = 5432
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    class Config:
        env_file = './database/.env'


settings = Settings()

POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
