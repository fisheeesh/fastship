from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field

# * SQL modal to represent database tables
# * We created SQL model to define data in the tables
# * Use these models to get data or send data to the database as well


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: int = Field(default=None, primary_key=True)
    content: str
    weight: float = Field(le=25, ge=1)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime
