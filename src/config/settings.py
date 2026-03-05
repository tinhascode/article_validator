from functools import lru_cache
from typing import Generator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expires_minutes: int
    jwt_refresh_token_expires_days: int
    jwt_refresh_cookie_name: str | None = None
    jwt_refresh_cookie_domain: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
    )

@lru_cache
def get_sessionmaker() -> sessionmaker:
    return sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    
    
)

def get_db() -> Generator[Session, None, None]:
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)