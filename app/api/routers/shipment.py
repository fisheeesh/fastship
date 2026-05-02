from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from app.utils import TEMPLATE_DIR

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

templates = Jinja2Templates(TEMPLATE_DIR)


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
    request: Request,
    id: UUID,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)

    context = shipment.model_dump()

    context["partner"] = shipment.delivery_partner.name
    context["status"] = shipment.status
    context["timeline"] = shipment.timeline

    context["timeline"].reverse()

    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context,
    )
