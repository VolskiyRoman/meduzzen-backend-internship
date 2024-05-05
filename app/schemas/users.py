from typing import List

from pydantic import BaseModel, EmailStr, constr


class BaseUserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
        from_attributes = True


class UserSchema(BaseUserSchema):
    password: str


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: str = None
    password: str = None


class UsersListResponse(BaseModel):
    users: List[BaseUserSchema]

    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {"id": 1, "username": "user1", "email": "user1@example.com"},
                    {"id": 2, "username": "user2", "email": "user2@example.com"},
                ]
            }
        }


class UserDetailResponse(BaseUserSchema):
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
