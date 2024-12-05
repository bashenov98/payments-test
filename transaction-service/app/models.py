from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, Numeric
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    currency = Column(String, nullable=False)
    balance = Column(Numeric(precision=12, scale=2), default=Decimal('0.00'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"))
    to_account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Float)
    status = Column(String, default="pending")

    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
