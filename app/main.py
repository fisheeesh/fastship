from typing import Any, Dict

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from .schemas import Shipment

app = FastAPI()


@app.get("/shipment/latest")
def get_latest_shipment():
    return {
        "id": "2132432",
        "weight": 1.24,
        "content": "glassware",
        "status": "out for delivery",
    }


@app.get("/shipment")
def get_shipment(id: int) -> Dict[str, Any]:
    return {
        "id": id,
        "weight": 1.24,
        "content": "wooden talbe",
        "status": "in transit",
    }


@app.post("/shipment")
def create_shipment(body: Shipment) -> Dict[str, Any]:
    return {
        "content": body.content,
        "weight": body.weight,
        "destination": body.destination,
    }


@app.put("/shipment")
def update_shipment():
    pass


@app.delete("/shipment")
def delete_shipment():
    pass


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
