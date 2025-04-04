from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    SECRET_KEY: str
    BASE_URL: str
    class Config:
        env_file = "app/.env"

settings = Settings()
