from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from ..config import db_settings

# * Create a database engine to connect with database
engine = create_async_engine(
    # * database type/dialect and file name
    url=db_settings.POSTGRES_URL,
    # * Log sql queries
    echo=True,
)


async def create_db_tables():
    async with engine.begin() as connection:
        from .models import Seller, Shipment  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all)


# * Session to interact with database
async def get_session():
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
