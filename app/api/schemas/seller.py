from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class BaseSeller(BaseModel):
    name: str
    email: EmailStr
    address: str
    zip_code: int


class SellerRead(BaseSeller):
    pass


class SellerCreate(BaseSeller):
    password: str


class SellerUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    zip_code: Optional[int] = Field(default=None)
