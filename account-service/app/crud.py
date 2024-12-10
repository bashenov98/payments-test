# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from . import models, schemas
from decimal import Decimal
import json

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
    user = db.query(models.User).filter(models.User.username == username).first()
    print(f"Fetched user for username '{username}': {user}")
    return user

def process_transaction(db: Session, body):
    """
    Process a transaction and validate its ID.
    """
    try:
        data = json.loads(body.decode())
        from_account_id = data.get("from_account_id")
        to_account_id = data.get("to_account_id")
        if not from_account_id:
            raise ValueError("from_account_id ID is required")

        if not to_account_id:
            raise ValueError("to_account_id ID is required")
        
        amount = data.get("amount")
        if amount is None:
            raise ValueError("Amount is required")
        
        # Fetch the transaction by ID
        from_account_id_ = db.query(models.Account).filter(models.Account.id == from_account_id).first()
        if not from_account_id_:
            raise NoResultFound(f"from_account_id with ID {from_account_id} not found")
        
        # Fetch the transaction by ID
        to_account_id_ = db.query(models.Account).filter(models.Account.id == to_account_id).first()
        if not to_account_id_:
            raise NoResultFound(f"to_account_id with ID {to_account_id} not found")
        
        # Perform your transaction processing logic
        print("Processing transaction:", data)
        summ = from_account_id_.balance-float(data.get("amount"))
        if summ < 0:
            raise ValueError("Unsufficient amount")
        
        from_account_id_.balance=summ
        from_account_id_.draft=float(amount)

        to_account_id_.balance +=float(amount)
        
        db.commit()

    except Exception as e:
        print("Error:", e)
        db.rollback()
        raise e

def process_replenishment(db: Session, body):
    """
    Process a transaction and validate its ID.
    """
    try:
        data = json.loads(body.decode())
        print("data:", data)
        to_account_id = data.get("to_account_id")

        if not to_account_id:
            raise ValueError("to_account_id ID is required")
        
        amount = data.get("amount")
        if amount is None:
            raise ValueError("Amount is required")
        
        # Fetch the transaction by ID
        to_account_id_ = db.query(models.Account).filter(models.Account.id == to_account_id).first()
        if not to_account_id_:
            raise NoResultFound(f"to_account_id with ID {to_account_id} not found")
        
        # Perform your transaction processing logic
        print("Processing transaction:", data)

        to_account_id_.balance +=float(amount)
        
        db.commit()

    except Exception as e:
        print("Error:", e)
        db.rollback()
        raise e
    
    
def process_withdrawal(db: Session, body):
    """
    Process a transaction and validate its ID.
    """
    try:
        data = json.loads(body.decode())
        print("data:", data)
        from_account_id = data.get("from_account_id")
        print("from_account_id:", from_account_id)

        if not from_account_id:
            raise ValueError("from_account_id ID is required")
        
        amount = data.get("amount")
        if amount is None:
            raise ValueError("Amount is required")
        
        # Fetch the transaction by ID
        from_account_id_ = db.query(models.Account).filter(models.Account.id == from_account_id).first()
        if not from_account_id_:
            raise NoResultFound(f"from_account_id with ID {from_account_id} not found")
        
        # Perform your transaction processing logic
        print("Processing transaction:", data)

        from_account_id_.balance-=float(amount)
        from_account_id_.draft=float(amount)
        
        db.commit()

    except Exception as e:
        print("Error:", e)
        db.rollback()
        raise e