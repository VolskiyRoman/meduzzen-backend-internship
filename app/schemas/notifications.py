from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: int
    text: str
    is_read: bool
    company_member_id: int
