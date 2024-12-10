from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.sql import case
from app import models

def create_pending_replenishment(db: Session, from_: str , to_account_id: int, amount: float, currency: str , rate: str ):
    """
    Создание пополнения со статусом "pending".
    """
    try:
        replenishment = models.Replenishment(
            from_ = from_,
            to_account_id=to_account_id,
            amount=amount,
            currency=currency,
            rate=rate,
            status="pending",  # Статус "pending"
            message="Replenishment is pending"
        )
        db.add(replenishment)
        db.commit()
        db.refresh(replenishment)
        return replenishment

    except Exception as e:
        db.rollback()
        raise e


def create_pending_withdrawal(db: Session,to_: str, from_account_id: int, amount: float, currency: str = "USD", rate: str = "1.0"):
    """
    Создание снятия со статусом "pending".
    """
    try:
        withdrawal = models.Withdrawal(
            from_account_id=from_account_id,
            to_ = to_,
            amount=amount,
            currency=currency,
            rate=rate,
            status="pending",  # Статус "pending"
            message="Withdrawal is pending"
        )
        db.add(withdrawal)
        db.commit()
        db.refresh(withdrawal)
        return withdrawal

    except Exception as e:
        db.rollback()
        raise e

def create_pending_transaction(db: Session, from_account_id: int, to_account_id: int, amount: float, currency: str = "USD", rate: str = "1.0"):
    """
    Создание перевода со статусом "pending".
    """
    try:
        transaction = models.Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            currency=currency,
            rate=rate,
            status="pending",  # Статус "pending"
            message="Transaction is pending"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    except Exception as e:
        db.rollback()
        raise e

def update_replenishment_status(db: Session, replenishment_id: int, status: str, message: str):
    """
    Обновление статуса пополнения.
    """
    try:
        replenishment = db.query(models.Replenishment).filter(models.Replenishment.id == replenishment_id).first()
        if not replenishment:
            raise ValueError("Replenishment not found")

        replenishment.status = status
        replenishment.message = message
        db.commit()
        db.refresh(replenishment)
        return replenishment

    except Exception as e:
        db.rollback()
        raise e

def update_withdrawal_status(db: Session, withdrawal_id: int, status: str, message: str):
    """
    Обновление статуса снятия.
    """
    try:
        withdrawal = db.query(models.Withdrawal).filter(models.Withdrawal.id == withdrawal_id).first()
        if not withdrawal:
            raise ValueError("Withdrawal not found")

        withdrawal.status = status
        withdrawal.message = message
        db.commit()
        db.refresh(withdrawal)
        return withdrawal

    except Exception as e:
        db.rollback()
        raise e

def update_transaction_status(db: Session, transaction_id: int, status: str, message: str):
    """
    Обновление статуса перевода.
    """
    try:
        transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        transaction.status = status
        transaction.message = message
        db.commit()
        db.refresh(transaction)
        return transaction

    except Exception as e:
        db.rollback()
        raise e

def get_all_transactions(db: Session):
    """
    Получить все транзакции из всех таблиц: transactions, replenishment, withdrawal.
    """
    # Получить все записи из таблицы transactions
    transactions = db.query(models.Transaction).all()
    
    # Получить все записи из таблицы replenishment
    replenishments = db.query(models.Replenishment).all()
    
    # Получить все записи из таблицы withdrawal
    withdrawals = db.query(models.Withdrawal).all()
    
    # Возврат всех транзакций в виде списка словарей
    return {
        "transactions": transactions,
        "replenishments": replenishments,
        "withdrawals": withdrawals
    }


def get_transactions_by_account(db: Session, account_id: int):
    """
    Получить все транзакции для конкретного аккаунта из всех таблиц: transactions, replenishment, withdrawal.
    """
    # Транзакции между счетами (transactions)
    transactions = db.query(models.Transaction).filter(
        (models.Transaction.from_account_id == account_id) |
        (models.Transaction.to_account_id == account_id)
    ).all()
    
    # Пополнения на счет (replenishment)
    replenishments = db.query(models.Replenishment).filter(
        models.Replenishment.to_account_id == account_id
    ).all()
    
    # Снятия со счета (withdrawal)
    withdrawals = db.query(models.Withdrawal).filter(
        models.Withdrawal.from_account_id == account_id
    ).all()
    
    # Возвращаем данные в виде словаря
    return {
        "transactions": transactions,
        "replenishments": replenishments,
        "withdrawals": withdrawals
    }


def get_account_balance_with_drafts(db: Session, account_id: int):
    """
    Calculate saldo (final balance) and draft (pending transactions) for the given account,
    including transfers, replenishments, and withdrawals.
    """
    # Calculate saldo from transactions (completed)
    transaction_saldo = db.query(
        func.sum(
            case(
                (models.Transaction.from_account_id == account_id, -models.Transaction.amount),
                (models.Transaction.to_account_id == account_id, models.Transaction.amount),
                else_=0,
            )
        )
    ).filter(models.Transaction.status != "pending").scalar() or float(0)

    # Calculate saldo from replenishments (completed)
    replenishment_saldo = db.query(
        func.sum(models.Replenishment.amount)
    ).filter(
        models.Replenishment.to_account_id == account_id,
        models.Replenishment.status != "pending"
    ).scalar() or float(0)

    # Calculate saldo from withdrawals (completed)
    withdrawal_saldo = db.query(
        func.sum(models.Withdrawal.amount)
    ).filter(
        models.Withdrawal.from_account_id == account_id,
        models.Withdrawal.status != "pending"
    ).scalar() or float(0)

    # Combine saldo components
    saldo = transaction_saldo + replenishment_saldo - withdrawal_saldo
    saldo = max(float(0), saldo)  # Ensure saldo is always non-negative

    # Calculate drafts for transactions
    transaction_draft = db.query(
        func.sum(models.Transaction.amount)
    ).filter(
        models.Transaction.from_account_id == account_id,
        models.Transaction.status == "pending"
    ).scalar() or float(0)

    # Calculate drafts for withdrawals
    withdrawal_draft = db.query(
        func.sum(models.Withdrawal.amount)
    ).filter(
        models.Withdrawal.from_account_id == account_id,
        models.Withdrawal.status == "pending"
    ).scalar() or float(0)

    # Combine draft components
    draft = transaction_draft + withdrawal_draft

    return {
        "saldo": saldo,
        "draft": draft
    }


def get_account_by_user_id(db: Session, user_id: int, account_id: int):
    try:
        return 1
    except Exception as e:
        db.rollback()
    raise e

def get_user_by_username(db: Session, username: str):
    return 1