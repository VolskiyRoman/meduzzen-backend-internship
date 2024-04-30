from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.repositories.company_repository import CompanyRepository
from app.schemas.companies import CompanySchema, CompanyCreateRequest, CompanyUpdateRequest, CompaniesListResponse
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.company_service import CompanyService

router = APIRouter(tags=["Companies"])


async def get_company_service(session: AsyncSession = Depends(get_async_session)) -> CompanyService:
    company_repository = CompanyRepository(session)
    return CompanyService(session=session, repository=company_repository)


@router.post("/", response_model=CompanySchema)
async def create_company(company_data: CompanyCreateRequest,
                         current_user: UserSchema = Depends(AuthService.get_current_user),
                         company_service: CompanyService = Depends(get_company_service)) -> CompanySchema:
    current_user_id = current_user.id
    return await company_service.create_company(company_data.model_dump(), current_user_id)


@router.patch("/{company_id}/", response_model=CompanySchema)
async def edit_company(company_id: int,
                       company_data: CompanyUpdateRequest,
                       current_user: UserSchema = Depends(AuthService.get_current_user),
                       company_service: CompanyService = Depends(get_company_service)) -> CompanySchema:
    current_user_id = current_user.id
    return await company_service.edit_company(company_data.model_dump(), current_user_id, company_id)


@router.delete("/{company_id}/", response_model=dict)
async def delete_company(company_id: int,
                         current_user: UserSchema = Depends(AuthService.get_current_user),
                         company_service: CompanyService = Depends(get_company_service)) -> dict:
    current_user_id = current_user.id
    return await company_service.delete_company(company_id, current_user_id)


@router.get("/{company_id}/", response_model=CompanySchema)
async def get_company_by_id(company_id: int,
                            current_user: UserSchema = Depends(AuthService.get_current_user),
                            company_service: CompanyService = Depends(get_company_service)) -> CompanySchema:
    current_user_id = current_user.id
    return await company_service.get_company_by_id(company_id, current_user_id)


@router.get('/', response_model=CompaniesListResponse)
async def get_all_companies(company_service: CompanyService = Depends(get_company_service),
                            current_user: UserSchema = Depends(AuthService.get_current_user),):
    return await company_service.get_companies()
