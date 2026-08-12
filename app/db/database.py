from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..core.config import DATABASE_URL
import os

assert DATABASE_URL, (
    os.getenv("DATABASE_URL")
)

engine = create_async_engine(DATABASE_URL, echo=True)

# Async session factory - connects with PostgreSQL asynchronously
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()  # Base factory for ORM models
