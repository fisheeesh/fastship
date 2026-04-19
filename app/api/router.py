from fastapi import APIRouter

from ..database.models import Shipment
from .dependencies import ServiceDep
from .schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)

router = APIRouter()


# ! FastAPI only looks for dependencies inside of the endpoints, not anywhere else
### Read a shipment by id
@router.get("/shipment/{id}", response_model=ShipmentRead)
async def get_shipment(
    id: int,
    service: ServiceDep,
):
    shipment = await service.get(id)

    return shipment


### Create new shipment
@router.post("/shipment", response_model=Shipment)
async def create_shipment(
    shipment_create: ShipmentCreate,
    service: ServiceDep,
):
    shipment = await service.add(shipment_create)

    return shipment


### Update a shipment by id
@router.patch("/shipment", response_model=Shipment)
async def update_shipment(
    id: int,
    shipment_update: ShipmentUpdate,
    service: ServiceDep,
):
    shipment = await service.update(id, shipment_update)

    return shipment


### Delete a shipment by id
@router.delete("/shipment", response_model=None)
async def delete_shipment(id: int, service: ServiceDep):
    await service.delete(id)

    return {"message": "Deleted successfully!"}
