from sqlalchemy import Column, String, DECIMAL, ForeignKey, TIMESTAMP
from database import Base
import 

class Notification(Base):
    __tablename__ = 'notification'
    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    account_id = Column(as_uuid=True), ForeignKey('accounts.account_id')
    notification = 
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
