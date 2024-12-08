from pydantic import BaseModel, Field

class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float = Field(gt=0, description="Amount must be greater than zero")

class TransactionResponse(BaseModel):
    id: int
    status: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
