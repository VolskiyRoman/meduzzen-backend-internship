from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.action_repository import ActionRepository


class ActionService:
    def __init__(self, session: AsyncSession, repository: ActionRepository):
        self.session = session
        self.repository = repository
