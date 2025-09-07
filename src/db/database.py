import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DATABASE_USER}:"
    f"{DATABASE_PASSWORD}@{DATABASE_HOST}:"
    f"{DATABASE_PORT}/{DATABASE_NAME}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    future=True,
)


async def get_db():
    async with SessionLocal() as session:
        yield session
