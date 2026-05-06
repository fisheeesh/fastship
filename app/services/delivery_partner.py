from typing import Sequence

from sqlalchemy import select

from ..core.exceptions import DeliveryPartnerNotAvailable
from ..api.schemas.delivery_partner import DeliveryPartnerCreate
from ..database.models import DeliveryPartner, Location, Shipment
from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session) -> None:
        super().__init__(DeliveryPartner, session)  # type: ignore

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        partner = await self._add_user(
            delivery_partner.model_dump(exclude={"servicable_zip_codes"}),
            "partner",
        )

        for zip_code in delivery_partner.servicable_zip_codes:
            location = self.session.get(Location, zip_code)
            partner.servicable_locations.append(  # type: ignore
                location if location else Location(zip_code)  # type: ignore
            )

        return await self._update(partner)

    async def login(self, email, password) -> str:
        return await self._login(email, password)

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def get_partners_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner)
                .join(DeliveryPartner.servicable_locations)  # type: ignore
                .where(Location.zip_code == zipcode)  # type: ignore
            )
        ).all()

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partners_by_zipcode(shipment.destination)

        for partner in eligible_partners:
            if partner.free_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        raise DeliveryPartnerNotAvailable("No delivery partner available.")
