# app/models.py
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer, Numeric
from decimal import Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

from .database import Base  # Импортируйте Base из database.py

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
    balance = Column(Numeric(precision=12, scale=2), default=float('0.00'))
    draft = Column(Numeric(precision=12, scale=2), default=float('0.00'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")
