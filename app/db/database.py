from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import DATABASE_URL

assert DATABASE_URL, (
    "DATABASE_URL missing from .env - add e.g. "
    "DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/localguard"
)

engine = create_async_engine(DATABASE_URL, echo=True)

# Async session factory - connects with PostgreSQL asynchronously
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()  # Base factory for ORM models
