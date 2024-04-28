from typing import List

from pydantic import BaseModel
from app.enums.invite import InvitationStatus


class ActionBaseSchema(BaseModel):
    id: int


class ActionSchema(ActionBaseSchema):
    user_id: int
    company_id: int
    status: InvitationStatus


class InviteCreateSchema(BaseModel):
    user_id: int
    company_id: int


class RequestCreateSchema(BaseModel):
    company_id: int


class GetActionsResponseSchema(ActionBaseSchema):
    user_id: int
    user_username: str
