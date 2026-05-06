from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    print("\nStarting tests...")
    yield
    print("\nFinished!!!")
