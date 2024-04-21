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

    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: str

    private_key_path: Path = Path("app/certs/jwt-private.pem")
    public_key_path: Path = Path("app/certs/jwt-public.pem")
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15

    class Config:
        env_file = ".env"


settings = Settings()
