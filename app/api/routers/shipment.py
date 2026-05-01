from uuid import UUID

from fastapi import APIRouter, HTTPException, status

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
@router.post("/", response_model=ShipmentRead)
async def create_shipment(
    seller: CurrentSellerDep,
    shipment_create: ShipmentCreate,
    service: ShipmentServiceDep,
):
    return await service.add(shipment_create, seller)


### Update a shipment by id
# ! Only authorized delivery partner can edit shipment
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    partner: CurrentPartnerDep,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    # ? Make sure to exclude none fields
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update.",
        )

    return await service.update(id, shipment_update, partner)


### Cancel a shipment by id
@router.get("/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    seller: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)