from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.enums.invite import InvitationStatus
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.actions import ActionSchema, InviteCreateSchema, RequestCreateSchema, GetActionsResponseSchema
from app.schemas.companies import CompanySchema
from app.schemas.users import UserSchema
from app.utils import companies as companies_utils
from app.utils.companies import raise_already_in_company_exception


class ActionService:
    def __init__(
            self,
            session: AsyncSession,
            action_repository: ActionRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository
    ):
        self.session = session
        self.action_repository = action_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return company

    async def _get_user_or_raise(self, user_id: int) -> UserSchema:
        user = await self.user_repository.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def _get_action_or_raise(self, action_id: int) -> ActionSchema:
        action = await self.action_repository.get_one(id=action_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This action is not found",
            )
        return action

    async def _add_user_to_company(self, action_id: int) -> ActionSchema:
        update_data = {"status": InvitationStatus.ACCEPTED.value}
        return await self.action_repository.update_one(action_id, update_data)

    async def create_invite(self, action_data: InviteCreateSchema, current_user_id: int) -> ActionSchema:
        await self._get_user_or_raise(action_data.user_id)
        company = await self._get_company_or_raise(action_data.company_id)
        await companies_utils.check_company_owner(current_user_id, company.owner_id)

        if action_data.user_id == company.owner_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You can't invite yourself",
            )
        invite = await self.action_repository.get_one(company_id=company.id, user_id=action_data.user_id)
        if invite:
            if invite.status == InvitationStatus.INVITED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already invited",
                )
            elif invite.status == InvitationStatus.ACCEPTED:
                await raise_already_in_company_exception()
            elif invite.status == InvitationStatus.REQUESTED:
                return await self._add_user_to_company(invite.id)
        else:
            data = action_data.dict()
            data["status"] = InvitationStatus.INVITED.value
            return await self.action_repository.create_one(data=data)

    async def cancel_invite(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        company = await self._get_company_or_raise(action.company_id)
        await companies_utils.check_company_owner(current_user_id, company.owner_id)
        await companies_utils.check_invited(action.status)
        await self.action_repository.delete_one(action.id)
        return action

    async def _get_invite(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        await companies_utils.check_invited(action.status)
        return action

    async def accept_invite(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_invite(action_id, current_user_id)
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        await self._add_user_to_company(action_id)
        return action

    async def decline_invite(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_invite(action_id, current_user_id)
        await self.action_repository.delete_one(action.id)
        return action

    async def create_request(self, action_data: RequestCreateSchema, current_user_id: id) -> ActionSchema:
        company = await self._get_company_or_raise(action_data.company_id)
        request = await self.action_repository.get_one(company_id=company.id, user_id=current_user_id)
        if company.owner_id == current_user_id:
            await raise_already_in_company_exception()
        if request:
            if request.status == InvitationStatus.REQUESTED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You have already sent a request to this company",
                )
            elif request.status == InvitationStatus.ACCEPTED or request.status == InvitationStatus.PROMOTED:
                await raise_already_in_company_exception()
            elif request.status == InvitationStatus.INVITED:
                return await self._add_user_to_company(request.id)
        else:
            data = action_data.dict()
            data["status"] = InvitationStatus.REQUESTED.value
            data["user_id"] = current_user_id
            return await self.action_repository.create_one(data=data)

    async def cancel_request(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        await companies_utils.check_requested(action.status)
        await companies_utils.check_correct_user(action.user_id, current_user_id)
        await self.action_repository.delete_one(action.id)
        return action

    async def _validate_request(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        company = await self._get_company_or_raise(action.company_id)
        await companies_utils.check_company_owner(current_user_id, company.owner_id)
        return action

    async def accept_request(self, action_id: int, current_user_id: int) -> ActionSchema:
        await self._validate_request(action_id, current_user_id)
        return await self._add_user_to_company(action_id)

    async def decline_request(self, action_id: int, current_user_id: int) -> ActionSchema:
        await self._validate_request(action_id, current_user_id)
        return await self.action_repository.delete_one(action_id)

    async def leave_from_company(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._get_action_or_raise(action_id)
        if current_user_id != action.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to leave this company",
            )
        return await self.action_repository.delete_one(action.id)

    async def kick_from_company(self, action_id: int, current_user_id: int) -> ActionSchema:
        action = await self._validate_request(action_id, current_user_id)
        return await self.action_repository.delete_one(action.id)

    async def _validate_company_get(self, current_user_id: int, company_id: Optional[int] = None) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        await companies_utils.check_company_owner(current_user_id, company.owner_id)
        return company

    async def get_company_invites(self,
                                  current_user_id: int,
                                  company_id: Optional[int] = None) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        invites = await self.action_repository.get_relatives(company_id,
                                                             InvitationStatus.INVITED,
                                                             is_company=True)
        return invites

    async def get_company_requests(self,
                                   current_user_id: int,
                                   company_id: Optional[int] = None) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        requests = await self.action_repository.get_relatives(company_id,
                                                              InvitationStatus.REQUESTED,
                                                              is_company=True)
        return requests

    async def get_company_members(self,
                                  current_user_id: int,
                                  company_id: Optional[int] = None) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        members = await self.action_repository.get_relatives(company_id,
                                                             InvitationStatus.ACCEPTED,
                                                             is_company=True)
        return members

    async def get_my_requests(self, current_user_id: int) -> List[GetActionsResponseSchema]:
        requests = await self.action_repository.get_relatives(current_user_id,
                                                              InvitationStatus.REQUESTED,
                                                              is_company=False)
        return requests

    async def get_my_invites(self, current_user_id: int) -> List[GetActionsResponseSchema]:
        invites = await self.action_repository.get_relatives(current_user_id,
                                                             InvitationStatus.INVITED,
                                                             is_company=False)
        return invites

    async def _validate_admin(self,
                              current_user_id: int,
                              company_id: int,
                              user_id: int,
                              validate_status: InvitationStatus) -> ActionSchema:
        company = await self._validate_company_get(current_user_id, company_id)
        action = await self.action_repository.get_one(company_id=company.id, user_id=user_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist",
            )
        if action.status != validate_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to make this user admin",
            )
        return action

    async def add_admin(self, current_user_id: int, company_id: int, user_id: int) -> ActionSchema:
        action = await self._validate_admin(current_user_id, company_id, user_id, InvitationStatus.ACCEPTED)
        action.status = InvitationStatus.PROMOTED
        return await self.action_repository.update_one(action.id, {'status': action.status})

    async def remove_admin(self, current_user_id: int, company_id: int, user_id: int) -> ActionSchema:
        action = await self._validate_admin(current_user_id, company_id, user_id, InvitationStatus.PROMOTED)
        action.status = InvitationStatus.ACCEPTED
        return await self.action_repository.update_one(action.id, {'status': action.status})

    async def get_admins(self, current_user_id: int, company_id: int) -> List[GetActionsResponseSchema]:
        await self._validate_company_get(current_user_id, company_id)
        return await self.action_repository.get_relatives(company_id, InvitationStatus.PROMOTED, is_company=True)

