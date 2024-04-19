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

    async def create_user(self, data: dict) -> UserSchema:
        email = data.get("email")
        existing_user_email = await self.repository.get_one(email=email)
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        username = data.get("username")
        existing_user_username = await self.repository.get_one(username=username)
        if existing_user_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists",
            )

        password = data.get("password")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        user = await self.repository.create_one(user_data)
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
