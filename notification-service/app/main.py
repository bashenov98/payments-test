# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Notification
from schemas import NotificationSend, NotificationResponse
from dependencies import get_db, get_current_user

app = FastAPI()

@app.post("/notifications", response_model=NotificationResponse)
def send_notification(
    notification: NotificationSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_notification = Notification(
        user_id=current_user.user_id,
        currency=account.currency
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification
