from datetime import datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..database.redis import get_shipment_verification_code

from .shipment_event import ShipmentEventService

from .base import BaseService
from .delivery_partner import DeliveryPartnerService

from ..api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from ..database.models import DeliveryPartner, Seller, Shipment, ShipmentStatus


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)  # type: ignore
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment:
        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment with given id does not exist.",
            )

        return shipment

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            # seller=Seller,
        )
        # * Assign delivery partner to the shipment
        partner = await self.partner_service.assign_shipment(new_shipment)
        # * Add the delivery partner foregin key
        new_shipment.delivery_partner_id = partner.id

        shipment = cast(Shipment, await self._add(new_shipment))

        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name}.",
        )

        shipment.timeline.append(event)

        return shipment

    async def update(
        self,
        id: UUID,
        shipment_update: ShipmentUpdate,
        partner: DeliveryPartner,
    ) -> Shipment:

        # ? Validate logged in partner with assigned partner
        # ? on the shipment with given id
        shipment = await self.get(id)

        if shipment.status == ShipmentStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You cannot edit to cancelled shipment.",
            )

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        if shipment_update.status == ShipmentStatus.delivered:
            code = await get_shipment_verification_code(shipment.id)

            if code != shipment_update.verification_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Client not authorized.",
                )

        if shipment_update.estimated_delivery is not None:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        # ? Make sure to exclude none fields

        update = shipment_update.model_dump(
            exclude_none=True,
            exclude=["verification_code"], # type: ignore
        )
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update.",
            )

        if len(update) > 1 or not shipment_update.estimated_delivery:
            await self.event_service.add(
                shipment=shipment,
                **update,
            )

        return cast(Shipment, await self._update(shipment))

    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        # * Validate the seller
        shipment = await self.get(id)

        if shipment.status == ShipmentStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="This shipment is already cancelled.",
            )

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )
        shipment.timeline.append(event)
        shipment.estimated_delivery = None

        return cast(Shipment, await self._update(shipment))

    async def delete(self, id: UUID, seller: Seller) -> None:
        shipment = await self.get(id)

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        try:
            await self.event_service.delete_by_shipment(shipment.id)
            await self._delete(shipment)
        except Exception:
            await self.session.rollback()
            raise
