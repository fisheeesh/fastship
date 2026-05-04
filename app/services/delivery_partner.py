from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select, any_

from ..api.schemas.delivery_partner import DeliveryPartnerCreate
from ..database.models import DeliveryPartner, Shipment
from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session) -> None:
        super().__init__(DeliveryPartner, session)  # type: ignore

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump(), "partner")

    async def login(self, email, password) -> str:
        return await self._login(email, password)

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def get_partners_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.serviceable_zip_codes)  # type: ignore
                )
            )
        ).all()

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partners_by_zipcode(shipment.destination)

        for partner in eligible_partners:
            if partner.free_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available.",
        )
