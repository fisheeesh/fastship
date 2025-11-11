from pydantic import BaseModel, EmailStr, Field


class BaseSeller(BaseModel):
    name: str
    email: EmailStr


class SellerRead(BaseSeller):
    pass


class SellerCreate(BaseSeller):
    password: str
