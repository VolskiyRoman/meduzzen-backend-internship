from app.repositories.user_repository import user_repository
from app.db.connection import async_session_maker
from fastapi import HTTPException, status


class UserService:
    @staticmethod
    async def create_one(data: dict):
        async with async_session_maker() as session:
            email = data.get("email")
            existing_user_email = await user_repository.get_one(session=session, email=email)
            if existing_user_email is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists",
                )

            username = data.get("username")
            existing_user_username = await user_repository.get_one(session=session, username=username)
            if existing_user_username is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists",
                )

            user = await user_repository.create_one(session=session, data=data)
            return user



user_service = UserService()
