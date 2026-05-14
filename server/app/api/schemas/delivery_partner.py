from typing import Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseDeliveryPartner(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    servicable_zip_codes: list[int]
    max_handling_capacity: int


class DeliveryPartnerRead(BaseDeliveryPartner):
    pass


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str


class DeliveryPartnerUPdate(BaseModel):
    servicable_zip_codes: Union[list[int], None] = Field(default=None)
    max_handling_capacity: Union[int, None] = Field(default=None)


class Shipment(BaseModel):
    content: str


class DeliveryPartnerShipments(BaseModel):
    shipments: list[Shipment]
    total_shipments: int
    page: int
    total_pages: int
