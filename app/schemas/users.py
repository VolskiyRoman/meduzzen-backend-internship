from typing import List

from pydantic import BaseModel, EmailStr

from app.db.models import User


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    is_admin: bool

    class Config:
        orm_mode = True


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: str
    email: EmailStr


class UsersListResponse(BaseModel):
    users: List[User]

    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {"id": 1, "username": "user1", "email": "user1@example.com"},
                    {"id": 2, "username": "user2", "email": "user2@example.com"},
                ]
            }
        }


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "user1",
                "email": "user1@example.com",
                "is_admin": True
            }
        }
