from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference
from sqlmodel import Session

from app.database.session import create_db_tables, get_session
from database.models import Shipment

from .schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)


### Read a shipment by id
@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int, session: Session = Depends(get_session)):
    shipment = session.get(Shipment, id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist!"
        )

    return shipment


### Create new shipment
@app.post("/shipment", response_model=None)
def create_shipment(
    body: ShipmentCreate, session: Session = Depends(get_session)
) -> Dict[str, Any]:
    return {
        "content": body.content,
        "weight": body.weight,
        "destination": body.destination,
    }


@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, body: ShipmentUpdate):
    return {
        "id": id,
        "status": body,
    }


@app.delete("/shipment")
def delete_shipment(id: int) -> Dict[str, int]:
    return {"id": id}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
