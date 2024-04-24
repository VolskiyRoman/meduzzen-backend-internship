from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    HOST: str
    PORT: int
    RELOAD: bool

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    TOKEN_EXPIRATION: int

    AUTH0_SECRET: str
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ALGORITHMS: str
    AUTH0_USERNAME_PREFIX: str

    class Config:
        env_file = ".env"


settings = Settings()
