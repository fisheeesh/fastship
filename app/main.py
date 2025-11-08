from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference
from sqlmodel import Session

from app.database.models import Shipment
from app.schemas import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate

from .database.session import create_db_tables, get_session

# ? Dependency injection means providing data in our context, providing data to our endpoints
# ? Instead of creating a static db vari like before, we can instead get a fresh db session on each req
# ? And that by simply adding it to our handler function as an argument to create a session


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int, session: Session = Depends(get_session)) -> ShipmentRead:
    shipment = session.get(Shipment, id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Give id doesn't exits!",
        )

    return shipment


@app.post("/shipment", response_model=None)
def submit_shipment(
    shipment: ShipmentCreate, session: Session = Depends(get_session)
) -> dict[str, int]:
    
    return {"id": 1}


@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, shipment: ShipmentUpdate):
    return {"id": id}


@app.delete("/shipment")
def delete_shipment(id: int):
    return ShipmentRead(
        content="syp", weight=1.2, destination=11200, status=ShipmentStatus.placed
    )


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
