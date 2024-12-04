from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional

class AccountCreate(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD, EUR)")

class AccountResponse(BaseModel):
    account_id: UUID
    user_id: UUID
    currency: str
    balance: Decimal

    class Config:
        orm_mode = True

class TransferRequest(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Currency code for the amount")

class TransferResponse(BaseModel):
    transaction_id: UUID
    status: str

class User(BaseModel):
    user_id: UUID
    username: str
    role: str

    class Config:
        orm_mode = True
