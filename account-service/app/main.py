# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Account
from schemas import AccountCreate, AccountResponse
from dependencies import get_db, get_current_user

app = FastAPI()

@app.post("/accounts", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_account = Account(
        user_id=current_user.user_id,
        currency=account.currency
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
