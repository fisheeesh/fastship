import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DeliveryPartner, Location, Seller


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

SELLER = {
    "name": "RainForest",
    "email": "rainforest@xmailg.one",
    "password": "lovetrees",
    "address": "42 Canopy Lane",
    "zip_code": 11001,
}
DELIVERY_PARTNER = {
    "name": "PHL",
    "email": "phl@xmailg.one",
    "password": "tough",
    "max_handling_capacity": 50,
    "servicable_zip_codes": [11001, 11002, 11003, 11004, 11005],
}
SHIPMENT = {
    "content": "Bananas",
    "weight": 1.25,
    "destination": 11004,
    "client_contact_email": "py@xmailg.one",
}


async def create_test_data(session: AsyncSession):
    session.add(
        Seller(
            **SELLER,
            email_verified=True,
            password_hash=hash_password(SELLER["password"]),
        )
    )
    session.add(
        DeliveryPartner(
            **DELIVERY_PARTNER,
            email_verified=True,
            password_hash=hash_password(DELIVERY_PARTNER["password"]),
            servicable_locations=[
                Location(zip_code=zip_code)
                for zip_code in DELIVERY_PARTNER["servicable_zip_codes"]
            ],
        )
    )

    await session.commit()
