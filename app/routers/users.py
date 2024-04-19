from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserSchema, SignUpRequest, UsersListResponse, UserUpdateRequest, BaseUserSchema
from app.services.user_service import UserService

router = APIRouter(tags=["Users"])


async def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(session=session, repository=user_repository)


@router.post('/', response_model=UserSchema)
async def create_user(user_create: SignUpRequest,
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_create.model_dump())


@router.get('/', response_model=UsersListResponse)
async def get_all_users(user_service: UserService = Depends(get_user_service)):
    users = await user_service.get_users()
    return UsersListResponse(users=[UserSchema.from_orm(user) for user in users])


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user_by_id(user_id)
    return user


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user(user_id, update_data)
    return updated_user


@router.delete("/{user_id}", response_model=BaseUserSchema)
async def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    deleted_user = await user_service.delete_user(user_id)
    return deleted_user
