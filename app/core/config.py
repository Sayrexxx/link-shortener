from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    SECRET_KEY: str
    BASE_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 86400

    
class Config:
        env_file = ".env"

settings = Settings()
