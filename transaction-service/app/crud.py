from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models

def transfer_funds(db: Session, from_account_id: int, to_account_id: int, amount: float):
    try:
        from_account = db.query(models.Account).filter(models.Account.user_id == from_account_id).first()
        to_account = db.query(models.Account).filter(models.Account.user_id == to_account_id).first()

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