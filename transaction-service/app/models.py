from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, Numeric
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, )
    to_account_id = Column(Integer, )
    amount = Column(Float)
    status = Column(String, default="pending")
