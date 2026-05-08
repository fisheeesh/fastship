from httpx import AsyncClient

from app.utils import print_label
from app.tests import example


async def test_app(client: AsyncClient):
    response = await client.get("/")

    print_label(response.json())

    assert response.status_code == 200


async def test_seller_login(client: AsyncClient):
    response = await client.post(
        "/seller/login",
        data={
            "grant_type": "password",
            "username": example.SELLER["email"],
            "password": example.SELLER["password"],
        },
    )

    print_label(response.json())

    assert response.status_code == 200
    assert "access_token" in response.json()
