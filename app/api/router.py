from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from app.database.models import Shipment
from app.database.session import SessionDep
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate

router = APIRouter()


@router.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id: int, session: SessionDep):
    shipment = await session.get(Shipment, id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Give id doesn't exits!",
        )

    return shipment


@router.post("/shipment", response_model=None)
async def submit_shipment(shipment: ShipmentCreate, session: SessionDep) -> dict[str, int]:
    new_shipment = Shipment(
        **shipment.model_dump(),
        status=ShipmentStatus.placed,
        estimated_delivery=datetime.now() + timedelta(days=3),
    )
    session.add(new_shipment)
    await session.commit()
    await session.refresh(new_shipment)

    return {"id": new_shipment.id}


@router.patch("/shipment", response_model=ShipmentRead)
async def update_shipment(id: int, shipment_update: ShipmentUpdate, session: SessionDep):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    shipment = await session.get(Shipment, id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    shipment.sqlmodel_update(update)
    session.add(shipment)
    await session.commit()
    await session.refresh(shipment)

    return shipment


@router.delete("/shipment")
async def delete_shipment(id: int, session: SessionDep):
    await session.delete(
        session.get(Shipment, id),
    )
    await session.commit()

    return {"detail": f"Shipment with id #{id} is deleted!"}
