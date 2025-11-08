from pydantic import BaseModel, Field
from app.database.models import ShipmentStatus

# * Pydantic model for schemas

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
