# app/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from jose import JWTError, jwt
from . import schemas
from .config import settings
from .crud import get_user_by_username
from fastapi.security import OAuth2PasswordBearer


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: schemas.TokenData = Depends(get_current_user)):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return current_user
