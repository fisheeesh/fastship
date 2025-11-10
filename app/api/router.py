from fastapi import APIRouter, HTTPException, status

from app.database.models import Shipment
from app.database.session import SessionDep
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)
from app.services.shipment import ShipmentService

router = APIRouter()


### Read a shipment by id
@router.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id: int, session: SessionDep):
    shipment = await ShipmentService(session).get(id)

    return shipment


### Create a new shipment
@router.post("/shipment")
async def submit_shipment(
    shipment_create: ShipmentCreate, session: SessionDep
) -> Shipment:
    return await ShipmentService(session).add(shipment_create)


### Update a shipment by id
@router.patch("/shipment", response_model=ShipmentRead)
async def update_shipment(
    id: int, shipment_update: ShipmentUpdate, session: SessionDep
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await ShipmentService(session).update(id, shipment_update)


### Delete a shipment by id
@router.delete("/shipment")
async def delete_shipment(id: int, session: SessionDep):
    await ShipmentService(session).delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}
