# app/routers/accounts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import json
from .. import schemas, crud, models
from ..dependencies import get_db, get_current_user, is_admin

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
def create_account(
    account: schemas.AccountCreate,
    db: Session = Depends(get_db),
    role_id: int = Depends(is_admin),
    current_user: int = Depends(get_current_user)
):
    return crud.create_account(db=db, account=account, user_id=current_user)

@router.get("/{account_id}", response_model=schemas.AccountOut)
def read_account(account_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None or db_account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.get("/users/{user_id}", response_model=List[schemas.AccountOut])
def read_accounts_by_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.id != user_id:
        # Здесь можно добавить проверку на администратора
        raise HTTPException(status_code=403, detail="Not enough permissions")
    accounts = crud.get_accounts_by_user(db, user_id=user_id)
    return accounts


"""
@router.put("/{account_id}/balance", response_model=schemas.AccountOut)
def update_account_balance(account_id: int, balance_update: schemas.BalanceUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    account = crud.get_account(db, account_id=account_id)
    if account is None or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    updated_account = crud.update_balance(db, account_id, balance_update.amount, balance_update.operation)
    if updated_account is None:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    return updated_account
"""
@router.get("/{account_id}/balance", response_model=schemas.BalanceResponse)
def get_account_balance(account_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    account = crud.get_account(db, account_id=account_id)
    if account is None or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return schemas.BalanceResponse(balance=account.balance)

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    account = crud.get_account(db, account_id=account_id)
    if account is None or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.balance != 0:
        raise HTTPException(status_code=400, detail="Balance must be zero to close the account")
    crud.delete_account(db, account_id=account_id)
    return {"detail": "Account deleted"}


def Operation (body, db: Session = Depends(get_db)):
    try:
        print("Unknown db:", db)
        # Decode the JSON object
        transaction = json.loads(body.decode())
        # Get the name field
        name = transaction.get("name")
        if name == "transactions":
            crud.process_transaction(db,body=body)
        elif name == "replenishment":
            crud.process_replenishment(db,body=body)
        elif name == "withdrawal":
            crud.process_withdrawal(db,body=body)
        else:
            print("Unknown name:", name)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except Exception as e:
        print(f"Error processing transaction: {e}")