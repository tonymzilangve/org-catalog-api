from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "org_db"
    DATABASE_URL: Optional[str] = None

    API_KEY: str = "AIzaSyD9kK8fJxQ4nL3pR7sT2vW1yZ0cB8nM6jK5lP4q7tH"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
