from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import ServiceDep
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)
from app.database.models import Shipment

router = APIRouter()


### Read a shipment by id
@router.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id: int, service: ServiceDep):
    shipment = await service.get(id)

    return shipment


### Create a new shipment
@router.post("/shipment")
async def submit_shipment(
    shipment_create: ShipmentCreate, service: ServiceDep
) -> Shipment:
    return await service.add(shipment_create)


### Update a shipment by id
@router.patch("/shipment", response_model=ShipmentRead)
async def update_shipment(
    id: int, shipment_update: ShipmentUpdate, service: ServiceDep
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, update)


### Delete a shipment by id
@router.delete("/shipment")
async def delete_shipment(id: int, service: ServiceDep):
    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}
