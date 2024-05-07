from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: int
    text: str
    is_read: bool
    user_id: int
