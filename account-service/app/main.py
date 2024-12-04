# app/main.py
from fastapi import FastAPI
from .routers import accounts
from .database import engine
from . import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Account Service API",
    description="API для управления счетами пользователей",
    version="1.0.0",
)

app.include_router(accounts.router)
