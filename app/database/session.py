from fastapi import Depends
from sqlalchemy.ext.asyncio import creat_async_engine, AsyncSession  # type: ignore
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from typing import Annotated

from app.config import settings

# * Create a database engine to connect with database
engine = creat_async_engine(
    # * database type/dialect and file name
    url=settings.POSTGRES_URL,
    # * Log sql queries
    echo=True,
)


async def create_db_tables():
    async with engine.begin() as connection:
        from .models import Shipment  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all(bind=engine))


# * Session to interact with database
async def get_session():
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


# * Session Dependency Annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]
