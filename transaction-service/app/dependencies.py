# app/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal, get_db
from jose import JWTError, jwt
from . import schemas
from .config import settings
from .crud import get_user_by_username
from .crud import get_account_by_user_id
from .schemas import TransactionRequest
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_account(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), request: schemas.TransactionRequest = None):
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
    if request is not None:
         account = get_account_by_user_id(db, user_id = user.id, account_id = request.from_account_id)
    else:
        raise credentials_exception
        
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account