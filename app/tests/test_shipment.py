from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from httpx import AsyncClient

from app.database.models import Tag, TagName
from app.tests import example
from app.utils import generate_url_safe_token

base_url = "/shipment/"


async def _create_shipment(client: AsyncClient, seller_token: str) -> dict:
    response = await client.post(
        base_url,
        json=example.SHIPMENT,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 201
    return response.json()


async def _ensure_tag(session: AsyncSession, tag_name: TagName) -> None:
    existing_tag = await session.scalar(select(Tag).where(Tag.name == tag_name))
    if existing_tag is not None:
        return

    session.add(
        Tag(
            name=tag_name,
            instruction=f"{tag_name.value.replace('_', ' ').title()} instructions.",
        )
    )
    await session.commit()


async def test_create_shipment_requires_seller_auth(client: AsyncClient):
    response = await client.post(base_url, json={})
    assert response.status_code == 401


async def test_create_and_get_shipment(client: AsyncClient, seller_token: str):
    shipment = await _create_shipment(client, seller_token)

    response = await client.get(
        base_url,
        params={"id": shipment["id"]},
    )
    assert response.status_code == 200
    assert response.json()["id"] == shipment["id"]


async def test_update_shipment_requires_partner_auth(
    client: AsyncClient, seller_token: str
):
    shipment = await _create_shipment(client, seller_token)
    response = await client.patch(
        base_url,
        params={"id": shipment["id"]},
        json={"status": "in_transit", "location": 11002},
    )

    assert response.status_code == 401


async def test_update_shipment(
    client: AsyncClient, seller_token: str, partner_token: str
):
    shipment = await _create_shipment(client, seller_token)

    response = await client.patch(
        base_url,
        params={"id": shipment["id"]},
        json={
            "status": "in_transit",
            "location": 11002,
            "description": "Reached transfer hub.",
        },
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert response.status_code == 200
    assert response.json()["timeline"][-1]["status"] == "in_transit"


async def test_delete_shipment(client: AsyncClient, seller_token: str):
    shipment = await _create_shipment(client, seller_token)

    response = await client.delete(
        base_url,
        params={"id": shipment["id"]},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 204

    response = await client.get(
        base_url,
        params={"id": shipment["id"]},
    )
    assert response.status_code == 404


async def test_cancel_shipment(client: AsyncClient, seller_token: str):
    shipment = await _create_shipment(client, seller_token)

    response = await client.post(
        "/shipment/cancel",
        params={"id": shipment["id"]},
        headers={"Authorization": f"Bearer {seller_token}"},
    )

    assert response.status_code == 200
    assert response.json()["timeline"][-1]["status"] == "cancelled"


async def test_get_review_form(client: AsyncClient):
    response = await client.get(
        "/shipment/review-form",
        params={"token": "sample-token"},
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


async def test_submit_review(client: AsyncClient, seller_token: str):
    shipment = await _create_shipment(client, seller_token)
    token = generate_url_safe_token({"id": shipment["id"]})

    response = await client.post(
        "/shipment/review",
        params={"token": token},
        data={"rating": "5", "comment": "Good service."},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Review Submitted! Thank you."


async def test_add_and_remove_shipment_tag(
    client: AsyncClient, seller_token: str, db_session: AsyncSession
):
    await _ensure_tag(db_session, TagName.STANDARD)
    shipment = await _create_shipment(client, seller_token)

    response = await client.get(
        "/shipment/tag",
        params={"id": shipment["id"], "tag_name": TagName.STANDARD.value},
    )

    assert response.status_code == 200
    assert any(tag["name"] == TagName.STANDARD.value for tag in response.json()["tags"])

    response = await client.delete(
        "/shipment/tag",
        params={"id": shipment["id"], "tag_name": TagName.STANDARD.value},
    )

    assert response.status_code == 200
    assert all(tag["name"] != TagName.STANDARD.value for tag in response.json()["tags"])


async def test_get_shipments_with_tag(
    client: AsyncClient, seller_token: str, db_session: AsyncSession
):
    await _ensure_tag(db_session, TagName.EXPRESS)
    shipment = await _create_shipment(client, seller_token)

    response = await client.get(
        "/shipment/tag",
        params={"id": shipment["id"], "tag_name": TagName.EXPRESS.value},
    )
    assert response.status_code == 200

    response = await client.get(
        "/shipment/tagged",
        params={"tag_name": TagName.EXPRESS.value},
    )

    assert response.status_code == 200
    assert any(item["id"] == shipment["id"] for item in response.json())
