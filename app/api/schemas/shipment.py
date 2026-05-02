from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from ...database.models import ShipmentEvent, ShipmentStatus


class BaseShipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(le=25, ge=1)
    destination: int


class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime | None
    # seller: Seller


class ShipmentCreate(BaseShipment):
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class ShipmentUpdate(BaseModel):
    location: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    verification_code: Optional[str] = Field(default=None)
    status: Optional[ShipmentStatus] = Field(default=None)
    estimated_delivery: Optional[datetime] = Field(default=None)
