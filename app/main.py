from fastapi import FastAPI

from loguru import logger
from app.core.config import settings
from app.routers import healthcheck, db_healthcheck, users, auth, companies, actions, quizzes, result, analytics, \
    notifications
import uvicorn

app = FastAPI()


logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")

app.include_router(healthcheck.router)
app.include_router(db_healthcheck.router)
app.include_router(users.router, prefix="/users")
app.include_router(auth.router, prefix="/auth")
app.include_router(companies.router, prefix="/company")
app.include_router(actions.router, prefix="/actions")
app.include_router(quizzes.router, prefix="/quizzes")
app.include_router(result.router, prefix="/results")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(notifications.router, prefix="/notifications")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
