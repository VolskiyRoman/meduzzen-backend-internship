from fastapi import FastAPI
from app.core.config import settings
from app.routers import healthcheck
from app.routers import test_db
import uvicorn


app = FastAPI()

app.include_router(healthcheck.router)
app.include_router(test_db.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
