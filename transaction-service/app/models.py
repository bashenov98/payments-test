from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, Numeric
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    is_admin = Column(Integer, default=0)
    accounts = relationship("Account", back_populates="owner")

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,  ForeignKey('users.id'), index=True, nullable=False)
    currency = Column(String, nullable=False)
    balance = Column(Numeric(precision=12, scale=2), default=Decimal('0.00'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, )
    to_account_id = Column(Integer, )
    amount = Column(Float)
    status = Column(String, default="pending")

    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])

    def to_dict(self):
        return {
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "amount": self.amount,
            "status": self.status
        }