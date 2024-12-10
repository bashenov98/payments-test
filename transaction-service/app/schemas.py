from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float = Field(gt=0, description="Amount must be greater than zero")
    currency: str
    rate: Optional[str] = None
    status: Optional[str] = "pending"
    message: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class TransactionResponse(BaseModel):
    id: int
    from_account_id: Optional[int]
    to_account_id: Optional[int]
    amount: float
    currency: str
    rate: Optional[str]
    status: str
    message: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str



# Replenishment Schemas
class ReplenishmentRequest(BaseModel):
    from_: str
    to_account_id: int
    amount: float = Field(gt=0, description="Amount must be greater than zero")
    currency: str
    rate: Optional[str] = None
    status: Optional[str] = "pending"
    message: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ReplenishmentResponse(BaseModel):
    id: int
    from_: str
    to_account_id: int
    amount: float
    currency: str
    rate: str
    status: str
    message: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        orm_mode = True

# Withdrawal Schemas
class WithdrawalRequest(BaseModel):
    from_account_id: int
    to_: str
    amount: float = Field(gt=0, description="Amount must be greater than zero")
    currency: str
    rate: Optional[str] = None
    status: Optional[str] = "pending"
    message: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class WithdrawalResponse(BaseModel):
    id: int
    from_account_id: int
    to_: str
    amount: float
    currency: str
    rate: str
    status: str
    message: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        orm_mode = True
