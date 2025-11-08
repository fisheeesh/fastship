from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate, ShipmentStatus

app = FastAPI()


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int) -> ShipmentRead:
    return ShipmentRead(
        content="syp", weight=1.2, destination=11200, status=ShipmentStatus.placed
    )


@app.post("/shipment")
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
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
