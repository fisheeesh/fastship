from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse

from ..dependencies import (
    CurrentPartnerDep,
    CurrentSellerDep,
    ShipmentServiceDep,
)
from ..schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)

router = APIRouter(prefix="/shipment", tags=["Shipment"])


# ! FastAPI only looks for dependencies inside of the endpoints, not anywhere else
### Read a shipment by id
@router.get("/", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
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


### Delete a shipment by id
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    id: UUID,
    seller: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    await service.delete(id, seller)

    return {"message": f"Deleted shipment with {id} successfully!"}


### Cancel a shipment by id
@router.post("/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    seller: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)


### Track details of a shipment
@router.get("/track")
async def get_tracking(
    id: UUID,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)

    return HTMLResponse(
        content=f"<body><h1>Order #{shipment.id} : {shipment.status}</h1></body>"
    )
