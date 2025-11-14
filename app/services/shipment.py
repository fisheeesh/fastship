from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.shipment import ShipmentCreate
from app.database.models import Seller, Shipment, ShipmentStatus
from app.services.base import BaseService
from app.services.delivery_partner import DeliveryPartnerService


# * We need the database session to perform all these interactions
# * So we will go ahead and receive that when we initialize this service
# ! One thing to note here is that we cannot directly use a dependency in a place like this service
# ! cannot (session: SessionDep) cus fastAPI only looks for dependencies inside of the endpoints not anywhere else
class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService):
        super().__init__(Shipment, session)  # type: ignore
        self.partner_service = partner_service

    async def get(self, id: UUID) -> Shipment:
        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                detail="Give id does not exist!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return shipment

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            # seller=seller,
        )
        # * Assign newly created shipment to avaiable partner based on its destination
        await self.partner_service.assign_shipment(new_shipment)
        return await self._add(new_shipment)

    async def update(self, id: UUID, shipment_update: dict) -> Shipment:
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        return await self._update(shipment)

    async def delete(self, id: UUID) -> None:
        await self._delete(await self.get(id))
