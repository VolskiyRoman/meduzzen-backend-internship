from datetime import datetime, timedelta
from fastapi import HTTPException

import bcrypt
import jwt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.db.connection import get_async_session
from app.repositories.base_repository import BaseRepository


async def encode_jwt(
    payload: dict,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = settings.AUTH0_ALGORITHMS,
    expire_minutes: int = settings.TOKEN_EXPIRATION,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        client_secret,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = settings.AUTH0_ALGORITHMS,
) -> dict:
    decoded = jwt.decode(
        token,
        client_secret,
        algorithms=algorithm,
        audience=settings.AUTH0_API_AUDIENCE,
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode('utf-8'),
        hashed_password=hashed_password.encode('utf-8'),
    )
