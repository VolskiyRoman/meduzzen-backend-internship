from pydantic import BaseModel

from app.enums.invite import InvitationStatus, InvitationType, MemberStatus


class ActionBaseSchema(BaseModel):
    id: int


class ActionSchema(ActionBaseSchema):
    user_id: int
    company_id: int
    status: InvitationStatus
    type: InvitationType


class InviteCreateSchema(BaseModel):
    user_id: int
    company_id: int


class RequestCreateSchema(BaseModel):
    company_id: int


class GetActionsResponseSchema(ActionBaseSchema):
    user_id: int
    user_username: str


class CompanyMemberSchema(ActionBaseSchema):
    user_id: int
    company_id: int
    role: MemberStatus

    class Config:
        orm_mode = True
        from_attributes = True
