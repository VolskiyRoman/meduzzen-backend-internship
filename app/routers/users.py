from fastapi import APIRouter
from app.schemas.users import UserSchema, SignUpRequest
from app.services.user_service import user_service

router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/", response_model=UserSchema)
async def create_user(user_data: SignUpRequest):
    return await user_service.create_one(user_data.model_dump())
