from app.api.schemas.shipment import ShipmentCreate
from app.database.models import Shipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi import HTTPException, status


# * We need the database session to perform all these interactions
# * So we will go ahead and receive that when we initialize this service
# ! One thing to note here is that we cannot directly use a dependency in a place like this service
# ! cannot (session: SessionDep) cus fastAPI only looks for dependencies inside of the endpoints not anywhere else
class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment:
        shipment = await self.session.get(Shipment, id)
        if shipment is None:
            raise HTTPException(
                detail="Give id does not exist!",
                status_code=status.HTTP_404_NOT_FOUND,
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

    async def update(self, id: int, shipment_update: dict) -> Shipment:
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    async def delete(self, id: int) -> None:
        await self.session.delete(await self.get(id))
        await self.session.commit()
