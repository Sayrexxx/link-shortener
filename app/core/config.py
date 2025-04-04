import os
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    BASE_URL: str = os.getenv("BASE_URL")

    class Config:
        env_file = "app/.env"

settings = Settings()
