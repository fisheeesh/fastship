from typing import Sequence

from sqlalchemy import select

from ..core.exceptions import DeliveryPartnerNotAvailable
from ..api.schemas.delivery_partner import DeliveryPartnerCreate, DeliveryPartnerUPdate
from ..database.models import DeliveryPartner, Location, Shipment
from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session) -> None:
        super().__init__(DeliveryPartner, session)  # type: ignore

    async def _resolve_locations(self, zip_codes: list[int]) -> list[Location]:
        unique_zip_codes = list(dict.fromkeys(zip_codes))
        locations: list[Location] = []

        for zip_code in unique_zip_codes:
            location = await self.session.get(Location, zip_code)
            locations.append(location if location else Location(zip_code=zip_code))

        return locations

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        partner = await self._add_user(
            delivery_partner.model_dump(exclude={"servicable_zip_codes"}),
            "partner",
        )

        partner.servicable_locations = await self._resolve_locations(
            delivery_partner.servicable_zip_codes
        )

        return await self._update(partner)

    async def login(self, email, password) -> str:
        return await self._login(email, password)

    async def update(
        self,
        partner: DeliveryPartner,
        delivery_partner_update: DeliveryPartnerUPdate,
    ):
        if delivery_partner_update.max_handling_capacity is not None:
            partner.max_handling_capacity = delivery_partner_update.max_handling_capacity

        if delivery_partner_update.servicable_zip_codes is not None:
            partner.servicable_locations = await self._resolve_locations(
                delivery_partner_update.servicable_zip_codes
            )

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
