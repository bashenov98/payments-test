from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.sql import case
from app import models

def transfer_funds(db: Session, from_account_id: int, to_account_id: int, amount: float):
    try:
        from_account = db.query(models.Account).filter(models.Account.id == from_account_id).first()
        to_account = db.query(models.Account).filter(models.Account.id == to_account_id).first()

        if not from_account or not to_account:
            raise ValueError("One or both accounts not found")
        
        if from_account.balance < amount:
            raise ValueError("Insufficient funds")

        from_account.balance -= Decimal(str(amount))
        to_account.balance += Decimal(str(amount))

        # Логируем транзакцию
        transaction = models.Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            status="completed"
        )
        db.add(transaction)

        db.commit()  
        db.refresh(transaction)
        return transaction

    except Exception as e:
        db.rollback()
        raise e

def get_all_transactions(db: Session):
    """
    Получить все транзакции.
    """
    return db.query(models.Transaction).all()

def get_transactions_by_account(db: Session, account_id: int):
    """
    Получить все транзакции для конкретного аккаунта.
    """
    return db.query(models.Transaction).filter(
        (models.Transaction.from_account_id == account_id) | 
        (models.Transaction.to_account_id == account_id)
    ).all()


def get_account_by_user_id(db: Session, user_id: int, account_id: int):
    return db.query(models.Account).filter(models.Account.user_id == user_id, models.Account.id == account_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()




def get_account_balance_with_drafts(db, account_id: int):
    """
    Calculate saldo (final balance) and draft (pending transactions) for the given account.
    """
    # Calculate saldo
    saldo = db.query(
        func.sum(
            case(
                (models.Transaction.from_account_id == account_id, -models.Transaction.amount),
                (models.Transaction.to_account_id == account_id, models.Transaction.amount),
            )
        )
    ).filter(models.Transaction.status != "pending").scalar() or 0

    # Calculate draft
    draft = db.query(
        func.sum(models.Transaction.amount)
    ).filter(
        models.Transaction.from_account_id == account_id,
        models.Transaction.status == "pending"
    ).scalar() or 0

    return {
        "saldo": saldo,
        "draft": draft
    }