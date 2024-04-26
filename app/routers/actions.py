from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.repositories.action_repository import ActionRepository
from app.services.action_service import ActionService

router = APIRouter(tags=["Actions"])


async def get_action_service(session: AsyncSession = Depends(get_async_session)) -> ActionService:
    action_repository = ActionRepository(session)
    return ActionService(session=session, repository=action_repository)
