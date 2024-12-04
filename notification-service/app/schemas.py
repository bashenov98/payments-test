from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional

class NotificationSend(BaseModel):
    notification: str
class NotificationResponse(BaseModel):
    notification_id: UUID
    account_id: UUID
    user_id: UUID
    notification: str

    class Config:
        orm_mode = True

class User(BaseModel):
    user_id: UUID
    username: str
    role: str

    class Config:
        orm_mode = True
