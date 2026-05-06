import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.database.session import get_session
from app.main import app
from app.tests import example

engine = create_async_engine(url="sqlite+aiosqlite:///:memory:")

test_session = sessionmaker(
    bind=engine,  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore


async def get_session_override():
    async with test_session() as session:  # type: ignore
        yield session


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def seller_token(client: AsyncClient):
    response = await client.post(
        "/seller/login",
        data={
            "grant_type": "password",
            "username": example.SELLER["email"],
            "password": example.SELLER["password"],
        },
    )

    assert "access_token" in response.json()
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="session")
async def partner_token(client: AsyncClient):
    response = await client.post(
        "/partner/login",
        data={
            "grant_type": "password",
            "username": example.DELIVERY_PARTNER["email"],
            "password": example.DELIVERY_PARTNER["password"],
        },
    )

    assert "access_token" in response.json()
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def db_session():
    async with test_session() as session:  # type: ignore
        yield session


@pytest.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    print("\nStarting tests...")

    from app.api import dependencies as api_dependencies

    original_is_jti_blacklisted = api_dependencies.is_jti_blacklisted

    async def is_jti_blacklisted_override(jti: str) -> bool:
        return False

    api_dependencies.is_jti_blacklisted = is_jti_blacklisted_override
    app.dependency_overrides[get_session] = get_session_override

    async with engine.begin() as connection:
        from app.database.models import Shipment, Seller, DeliveryPartner  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all)

    async with test_session() as session:  # type: ignore
        await example.create_test_data(session)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)

    app.dependency_overrides.clear()
    api_dependencies.is_jti_blacklisted = original_is_jti_blacklisted

    print("\nFinished!!!")
