from fastapi import FastAPI
from loguru import logger
from app.core.config import settings
from app.routers import healthcheck
from app.routers import db_healthcheck
import uvicorn


app = FastAPI()

logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")

app.include_router(healthcheck.router)
app.include_router(db_healthcheck.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
