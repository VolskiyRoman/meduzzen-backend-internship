from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


engine = create_engine(
    DATABASE_URL,
    pool_size=40,
    max_overflow=40,
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
