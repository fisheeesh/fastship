from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from .base import BaseService
from .delivery_partner import DeliveryPartnerService

from ..api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from ..database.models import Seller, Shipment, ShipmentStatus


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService):
        super().__init__(Shipment, session)  # type: ignore
        self.partner_service = partner_service

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
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            # seller=Seller,
        )

        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id
        return await self._add(new_shipment)  # type: ignore

    async def update(self, id: UUID, shipment_update: ShipmentUpdate) -> Shipment:
        # ? Make sure to exclude none fields
        update = shipment_update.model_dump(exclude_none=True)
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update.",
            )

        shipment = await self.get(id)
        shipment.sqlmodel_update(update)

        return await self._update(shipment)  # type: ignore

    async def delete(self, id: UUID) -> None:
        shipment = await self.get(id)

        await self._delete(shipment)
