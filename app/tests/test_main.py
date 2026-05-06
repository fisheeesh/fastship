from httpx import AsyncClient
import pytest


# @pytest.mark.asyncio
async def test_app(client: AsyncClient):
    response = await client.get("/")
    print("\n[Response]:", response.json())
    assert response.status_code == 200
