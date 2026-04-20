from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime
from pydantic import EmailStr


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime


class Seller(SQLModel, table=True):
    __tablename__ = "seller"  # type: ignore

    id: int = Field(primary_key=True, default=None)
    name: str
    email: EmailStr
    password_hash: str
