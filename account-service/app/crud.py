# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from decimal import Decimal

def create_account(db: Session, account: schemas.AccountCreate, user_id: int):
    db_account = models.Account(
        user_id=user_id,
        currency=account.currency,
        balance=0.0
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def get_accounts_by_user(db: Session, user_id: int):
    return db.query(models.Account).filter(models.Account.user_id == user_id).all()

def update_balance(db: Session, account_id: int, amount: Decimal, operation: str):
    account = get_account(db, account_id)
    if account is None:
        return None  # Аккаунт не найден
    if operation == "debit":
        if account.balance < amount:
            return None  # Недостаточно средств
        account.balance -= amount
    elif operation == "credit":
        account.balance += amount
    db.commit()
    db.refresh(account)
    return account

def delete_account(db: Session, account_id: int):
    account = get_account(db, account_id)
    if account is None:
        return None  # Аккаунт не найден
    if account.balance != 0:
        return None  # Баланс должен быть нулевым
    db.delete(account)
    db.commit()
    return True

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
