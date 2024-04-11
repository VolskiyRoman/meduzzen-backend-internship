from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import models
from app.db.connection import get_session
from app.routers import healthcheck
from app.routers import db_healthcheck
import uvicorn


app = FastAPI()

app.include_router(healthcheck.router)
app.include_router(db_healthcheck.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )


@app.get("/user", summary="Create a new user")
def create_user(db: Session = Depends(get_session)):
    new_user = models.User(username='123', email="<EMAIL>", password="<PASSWORD>", is_admin=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
