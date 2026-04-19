from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict

from .database.models import Shipment, ShipmentStatus
from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

from .database.session import SessionDep, create_db_tables

from .schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)


### Read a shipment by id
@app.get("/shipment/{id}", response_model=ShipmentRead)
async def get_shipment(id: int, session: SessionDep):
    shipment = await session.get(Shipment, id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist!"
        )

    return shipment


### Create new shipment
@app.post("/shipment", response_model=None)
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
@app.patch("/shipment", response_model=ShipmentRead)
async def update_shipment(id: int, shipment_update: ShipmentUpdate, session: SessionDep):
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
@app.delete("/shipment", response_model=None)
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


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
