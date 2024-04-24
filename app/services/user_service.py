from typing import List, Optional

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def _get_user_or_raise(self, user_id: int) -> UserSchema:
        user = await self.repository.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserSchema.from_orm(user)

    async def get_users(self, skip: int = 1, limit: int = 10) -> List[UserSchema]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        return users

    async def get_user_by_id(self, user_id: int) -> Optional[UserSchema]:
        return await self._get_user_or_raise(user_id)

    async def update_user(self, user_id: int, update_data: UserUpdateRequest) -> UserSchema:
        await self._get_user_or_raise(user_id)
        update_dict = update_data.dict(exclude_unset=True)
        updated_user = await self.repository.update_one(user_id, update_dict)
        return UserSchema.from_orm(updated_user)

    async def delete_user(self, user_id: int) -> BaseUserSchema:
        await self._get_user_or_raise(user_id)
        return await self.repository.delete_one(user_id)
