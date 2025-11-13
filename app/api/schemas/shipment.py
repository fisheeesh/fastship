from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.database.models import Seller, ShipmentStatus

# * Pydantic model for schemas
# * Use it for data validation in the request body and response data


class BaseShipment(BaseModel):
    content: str = Field(description="Content of the shipment", max_length=30)
    weight: float = Field(
        description="Weight of the shipment in kilograms(kg)", le=25, ge=1
    )
    destination: int = Field(
        description="Destination Zipcode. If not provided, will be sent off to a random location",
    )


class ShipmentRead(BaseShipment):
    id: UUID
    status: ShipmentStatus
    estimated_delivery: datetime
    seller: Seller


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
