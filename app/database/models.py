from datetime import datetime
from enum import Enum
from uuid import uuid4, UUID
from sqlmodel import Column, Relationship, SQLModel, Field
from pydantic import EmailStr
from sqlalchemy.dialects import postgresql

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

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4(),
            primary_key=True,
        ),
    )
    content: str
    weight: float = Field(le=25, ge=1)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime

    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Seller(SQLModel, table=True):
    __tablename__ = "seller"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4(),
            primary_key=True,
        )
    )
    name: str

    email: EmailStr
    password_hash: str

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
