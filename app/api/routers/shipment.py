from uuid import UUID

from fastapi import APIRouter

from ...database.models import Shipment
from ..dependencies import CurrentPartnerDep, CurrentSellerDep, ShipmentServiceDep
from ..schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)

router = APIRouter(prefix="/shipment", tags=["Shipment"])


# ! FastAPI only looks for dependencies inside of the endpoints, not anywhere else
### Read a shipment by id
@router.get("/{id}", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
    _: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    return await service.get(id)


### Create new shipment
@router.post("/", response_model=Shipment)
async def create_shipment(
    seller: CurrentSellerDep,
    shipment_create: ShipmentCreate,
    service: ShipmentServiceDep,
):
    return await service.add(shipment_create, seller)


### Update a shipment by id
# ! Only authorized delivery partner can edit shipment
@router.patch("/", response_model=Shipment)
async def update_shipment(
    id: UUID,
    _: CurrentPartnerDep,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    return await service.update(id, shipment_update)


### Delete a shipment by id
@router.delete("/", response_model=None)
async def delete_shipment(
    id: UUID,
    _: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    await service.delete(id)

    return {"message": "Deleted a shipment successfully!"}
