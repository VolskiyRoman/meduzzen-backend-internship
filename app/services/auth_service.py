from datetime import datetime
from http.client import HTTPException
from random import choices
from string import ascii_lowercase, digits

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from app.core.config import settings
from app.db.connection import get_async_session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenInfo
from app.utils import auth as auth_utils

security = HTTPBearer()


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def validate_auth_user(self, data: dict) -> TokenInfo:
        email = data.get("email")
        password = data.get("password")
        db_user = await self.repository.get_one(email=email)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email does not exist",
            )

        if not auth_utils.validate_password(
                password=password,
                hashed_password=db_user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect password",
            )
        token = await auth_utils.encode_jwt(payload={"email": email, "from": "noauth0"})
        token_info = TokenInfo(access_token=token, token_type="Bearer")
        return token_info

    async def create_user(self, data: dict) -> TokenInfo:
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
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )

        password = data.get("password")
        hashed_password = auth_utils.hash_password(password=password)

        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "is_admin": data.get("is_admin", False),
        }

        await self.repository.create_one(user_data)

        token = await auth_utils.encode_jwt(payload={"email": email})
        token_info = TokenInfo(access_token=token, token_type="Bearer")

        return token_info

    @staticmethod
    async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security),
                               session: AsyncSession = Depends(get_async_session)) -> str:
        decoded_token = auth_utils.decode_jwt(token.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token invalid",
            )

        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
        if current_time >= expiration_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        user_email = decoded_token.get("email")
        user_repository = UserRepository(session=session)
        current_user = await user_repository.get_one(email=user_email)

        if not current_user:
            username_prefix = settings.AUTH0_USERNAME_PREFIX
            random_suffix = ''.join(choices(ascii_lowercase + digits, k=6))
            username = username_prefix + random_suffix
            password = str(datetime.now())

            hashed_password = auth_utils.hash_password(password)

            user_data = {
                "email": user_email,
                "username": username,
                "password": hashed_password.decode("utf-8"),
                "is_admin": decoded_token.get("is_admin", False),
            }

            await user_repository.create_one(user_data)
            current_user = username

        return current_user
