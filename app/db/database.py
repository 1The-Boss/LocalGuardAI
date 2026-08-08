# from sqlalchemy import create_engine
# from app.core.config import DATABASE_URL
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


engine=create_async_engine(DATABASE_URL, echo=True)

# Async session factory - connects with PostgreSQL asynchronously
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base=declarative_base() # Base factory for ORM models
print(DATABASE_URL)
