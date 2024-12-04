from sqlalchemy import Column, String, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid

class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    currency = Column(String(3), nullable=False)
    balance = Column(DECIMAL, default=0.0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
