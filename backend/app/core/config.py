import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthLens AI API"
    API_V1_STR: str = "/api"
    
    # Security
    JWT_SECRET: str = "supersecretjwtkeyforprototype12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # DB
    DATABASE_URL: str = "sqlite:///./truthlens.db"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # APIs Keys
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    MEDIASTACK_API_KEY: Optional[str] = None
    HIVE_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# DB Engine and Session Setup
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

