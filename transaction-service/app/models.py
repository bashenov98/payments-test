from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, Numeric
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, )
    to_account_id = Column(Integer, )
    amount = Column(Float)
    currency = Column(String)
    rate = Column(String)
    status = Column(String, default="pending")
    message = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary."""
        return {
            "name" : "transactions",
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "amount": self.amount,
            "currency": self.currency,
            "rate": self.rate,
            "status": self.status,
            "message": self.message,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }

class Replenishment(Base):
    __tablename__ = "replenishment"

    id = Column(Integer, primary_key=True, index=True)
    from_ = Column(String)
    to_account_id = Column(Integer, )
    amount = Column(Float)
    currency = Column(String)
    rate = Column(String)
    status = Column(String, default="pending")
    message = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary."""
        return {
            "name" : "replenishment",
            "id": self.id,
            "from": self.from_,
            "to_account_id": self.to_account_id,
            "amount": self.amount,
            "currency": self.currency,
            "rate": self.rate,
            "status": self.status,
            "message": self.message,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }

class Withdrawal(Base):
    __tablename__ = "withdrawal"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, )
    to_ = Column(String)
    amount = Column(Float)
    currency = Column(String)
    rate = Column(String)
    status = Column(String, default="pending")
    message = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary."""
        return {
            "name" : "withdrawal",
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to": self.to_,
            "amount": self.amount,
            "currency": self.currency,
            "rate": self.rate,
            "status": self.status,
            "message": self.message,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }
    