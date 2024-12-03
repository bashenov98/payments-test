# config.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Database settings
    DB_USERNAME: str = Field(..., env='DB_USERNAME')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    DB_HOST: str = Field(default='localhost', env='DB_HOST')
    DB_PORT: int = Field(default=5432, env='DB_PORT')
    DB_NAME: str = Field(..., env='DB_NAME')

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = Field(default='HS256', env='JWT_ALGORITHM')

    # Application settings
    APP_NAME: str = Field(default='AccountService')
    DEBUG: bool = Field(default=False, env='DEBUG')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
