from api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from database.models import Shipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi import HTTPException, status


class ShipmentService:
    def __int__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment:
        shipment = await self.session.get(Shipment, id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment with given id does not exist.",
            )

        return shipment

    async def add(self, shipment_create: ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
        )

        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)

        return new_shipment

    async def update(self, id: int, shipment_update: ShipmentUpdate) -> Shipment:
        # ? Make sure to exclude none fields
        update = shipment_update.model_dump(exclude_none=True)
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update.",
            )

        shipment = await self.get(id)

        shipment.sqlmodel_update(update)
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    async def delete(self, id: int) -> None:
        shipment = await self.get(id)

        await self.session.delete(shipment)
        await self.session.commit()
