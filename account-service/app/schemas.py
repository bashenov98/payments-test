# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class AccountBase(BaseModel):
    currency: str

class AccountCreate(AccountBase):
    pass

class AccountOut(AccountBase):
    id: int
    user_id: int  
    balance: Decimal

    class Config:
        orm_mode=True


class BalanceUpdate(BaseModel):
    amount: Decimal
    operation: str  

class BalanceResponse(BaseModel):
    balance: Decimal

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
