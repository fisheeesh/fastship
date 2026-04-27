from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlmodel import Relationship, SQLModel, Field
from enum import Enum
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.dialects import postgresql


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime

    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Seller(SQLModel, table=True):
    __tablename__ = "seller"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            primary_key=True,
            default=uuid4,
        )
    )
    name: str
    address: int
    email: EmailStr
    password_hash: str

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        # ? This will ensure when we access the shipments on the seller field,
        # ? it actually goes ahead and selects the data from the database
        # ? that is all the shipments with their seller id and give us back the same
        sa_relationship_kwargs={"lazy": "selectin"},
    )
