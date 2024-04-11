import logging
import os
from urllib.request import Request

from fastapi import FastAPI

from app.core.config import settings
from app.routers import healthcheck
from app.routers import db_healthcheck
import uvicorn


app = FastAPI()

log_file_path = os.path.join(os.path.dirname(__file__), '..', 'api.log')
print(f"Путь к файлу логов: {log_file_path}")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="api.log",
    filemode="a"
)
logger = logging.getLogger("uvicorn")

logger.setLevel(logging.DEBUG)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request received: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response returned: {response.status_code}")
    return response

app.include_router(healthcheck.router)
app.include_router(db_healthcheck.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )


