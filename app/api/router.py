from datetime import datetime, timedelta
from typing import Dict

from database.models import Shipment
from database.session import SessionDep
from fastapi import APIRouter, HTTPException, status
from api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentStatus,
    ShipmentUpdate,
)
from services.shipment import ShipmentService

router = APIRouter()


### Read a shipment by id
@router.get("/shipment/{id}", response_model=ShipmentRead)
async def get_shipment(id: int, session: SessionDep):
    shipment = await ShipmentService(session).get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist!"
        )

    return shipment


### Create new shipment
@router.post("/shipment", response_model=None)
async def create_shipment(
    shipment: ShipmentCreate, session: SessionDep
) -> Dict[str, int]:
    new_shipment = Shipment(
        **shipment.model_dump(),
        status=ShipmentStatus.placed,
        estimated_delivery=datetime.now() + timedelta(days=3),
    )

    session.add(new_shipment)
    await session.commit()
    await session.refresh(new_shipment)

    return {"id": new_shipment.id}


### Update a shipment by id
@router.patch("/shipment", response_model=ShipmentRead)
async def update_shipment(
    id: int, shipment_update: ShipmentUpdate, session: SessionDep
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update.",
        )

    shipment = await session.get(Shipment, id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist."
        )

    shipment.sqlmodel_update(update)
    session.add(shipment)
    await session.commit()
    await session.refresh(shipment)

    return shipment


### Delte a shipment by id
@router.delete("/shipment", response_model=None)
async def delete_shipment(id: int, session: SessionDep):
    shipment = await session.get(Shipment, id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist.",
        )

    await session.delete(shipment)
    await session.commit()

    return {"message": "Deleted successfully!"}
