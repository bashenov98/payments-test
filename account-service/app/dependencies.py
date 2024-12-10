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

def get_db_session():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e
    
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
        role_id: int = payload.get("role_id")
        user_id: int = payload.get("user_id")
        if username is None or role_id is None or user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, role_id=role_id, user_id=user_id)
    except JWTError:
        raise credentials_exception
    return user_id


def get_current_user_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"Token: {token}")  # Debugging
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Payload: {payload}")  # Debugging
        role_id: int = payload.get("role_id")
        if role_id is None:
            raise credentials_exception
        return role_id
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception
        

def is_admin(role_id: int = Depends(get_current_user_role)):
    print(f"Role: {role_id}")  # Debugging
    if role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough privileges",
        )


