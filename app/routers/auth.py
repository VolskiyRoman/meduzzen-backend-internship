from fastapi import (
    APIRouter,
    Depends,
)

from app.schemas.auth import TokenInfo
from app.schemas.users import SignInRequest, SignUpRequest, UserSchema
from app.services.auth_service import AuthService
from app.utils.call_services import get_auth_service

router = APIRouter(prefix="/jwt", tags=["JWT"])


@router.post("/login/", response_model=TokenInfo)
async def login_jwt(login_data: SignInRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.validate_auth_user(login_data.model_dump())


@router.post("/signup/", response_model=dict)
async def create_user(user_create: SignUpRequest,
                      user_service: AuthService = Depends(get_auth_service)):
    return await user_service.create_user(user_create.model_dump())


@router.get("/me", response_model=UserSchema)
async def get_current_user_route(current_user: UserSchema = Depends(AuthService.get_current_user)):
    return current_user

