from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

from ...database.models import ShipmentStatus


class BaseShipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(le=25, ge=1)
    destination: int


class ShipmentRead(BaseShipment):
    status: ShipmentStatus
    estimated_delivery: datetime


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    status: Optional[ShipmentStatus] = Field(default=None)
    estimated_delivery: Optional[datetime] = Field(default=None)
