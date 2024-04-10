from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session

router = APIRouter()


@router.get("/test_postgres")
async def check_postgres(session: AsyncSession = Depends(get_async_session)):
    return {
        "status_code": 200 if session else 500
    }


@router.get("/test_redis")
async def check_redis():
    return {
        "status_code": 200
    }
