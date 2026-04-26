from sqlmodel import Relationship, SQLModel, Field
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

    seller_id: int = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Seller(SQLModel, table=True):
    __tablename__ = "seller"  # type: ignore

    id: int = Field(primary_key=True, default=None)
    name: str
    email: EmailStr
    password_hash: str

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        # ? This will ensure when we access the shipments on the seller field,
        # ? it actually goes ahead and selects the data from the database
        # ? that is all the shipments with their seller id and give us back the same
        sa_relationship_kwargs={"lazy": "selectin"},
    )
