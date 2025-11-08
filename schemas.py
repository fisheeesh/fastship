from enum import Enum
from pydantic import BaseModel, Field


class ShipmentStatus(Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class BaseShipment(BaseModel):
    content: str = Field(description="Content of the shipment", max_length=30)
    weight: float = Field(
        description="Weight of the shipment in kilograms(kg)", le=25, ge=1
    )
    destination: int = Field(
        description="Destination Zipcode. If not provided, will be sent off to a random location",
    )


class ShipmentRead(BaseShipment):
    status: ShipmentStatus


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus
