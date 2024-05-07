from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserSchema, UserUpdateRequest, BaseUserSchema
import app.utils.auth as auth_utils


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

    @staticmethod
    async def check_user_permission(user_id: int, current_user: UserSchema):
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this user",
            )

    async def update_user(self, user_id: int, update_data: UserUpdateRequest, current_user: UserSchema) -> UserSchema:
        await self.check_user_permission(user_id, current_user)
        await self._get_user_or_raise(user_id)
        existing_user = await self.repository.get_one(username=update_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken",
            )
        update_dict = update_data.dict(exclude_unset=True)
        if update_data.password:
            hashed_password = auth_utils.hash_password(update_dict['password'])
            update_dict['password'] = hashed_password.decode('utf-8')

        updated_user = await self.repository.update_one(user_id, update_dict)
        return UserSchema.from_orm(updated_user)

    async def delete_user(self, user_id: int, current_user: UserSchema) -> BaseUserSchema:
        await self.check_user_permission(user_id, current_user)
        await self._get_user_or_raise(user_id)
        return await self.repository.delete_one(user_id)
