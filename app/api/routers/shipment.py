from fastapi import APIRouter

from ...database.models import Shipment
from ..dependencies import CurrentSellerDep, ShipmentServiceDep
from ..schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
)

router = APIRouter(prefix="/shipment", tags=["Shipment"])


# ! FastAPI only looks for dependencies inside of the endpoints, not anywhere else
### Read a shipment by id
@router.get("/{id}", response_model=Shipment)
async def get_shipment(
    id: int,
    _: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)

    return shipment


### Create new shipment
@router.post("/", response_model=Shipment)
async def create_shipment(
    _: CurrentSellerDep,
    shipment_create: ShipmentCreate,
    service: ShipmentServiceDep,
):
    shipment = await service.add(shipment_create)

    return shipment


### Update a shipment by id
@router.patch("/", response_model=Shipment)
async def update_shipment(
    id: int,
    _: CurrentSellerDep,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    shipment = await service.update(id, shipment_update)

    return shipment


### Delete a shipment by id
@router.delete("/", response_model=None)
async def delete_shipment(
    id: int,
    _: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    await service.delete(id)

    return {"message": "Deleted successfully!"}
