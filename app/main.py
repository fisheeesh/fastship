from typing import Any, Dict

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from .schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate

app = FastAPI()


@app.get("/shipment/latest")
def get_latest_shipment():
    return {
        "id": "2132432",
        "weight": 1.24,
        "content": "glassware",
        "status": "out for delivery",
    }


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int):
    return {
        "id": id,
        "content": "hello",
        "weight": 1.23,
        # "destination": 11020,
        "status": "placed",
    }


@app.post("/shipment")
def create_shipment(body: ShipmentCreate) -> Dict[str, Any]:
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
