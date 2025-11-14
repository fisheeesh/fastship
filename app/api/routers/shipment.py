from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)
from app.database.models import Shipment

router = APIRouter(
    prefix="/shipment",
    tags=["Shipment"],
)


### Read a shipment by id
@router.get("/", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
    _: SellerDep,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)

    return shipment


### Create a new shipment
@router.post("/")
async def submit_shipment(
    seller: SellerDep,
    shipment_create: ShipmentCreate,
    service: ShipmentServiceDep,
) -> Shipment:
    return await service.add(shipment_create, seller)


### Update a shipment by id
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    # * Only logged in delivery partner can update shipment's status
    _: DeliveryPartnerDep,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, update)


### Delete a shipment by id
@router.delete("/")
async def delete_shipment(
    id: UUID,
    _: SellerDep,
    service: ShipmentServiceDep,
):
    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}
