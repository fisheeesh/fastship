from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import CurrentPartnerDep, verify_partner_access_token
from api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUPdate,
)
from database.redis import add_jti_to_blacklist


router = APIRouter(prefix="/partner", tags=["Delivery Partner"])


### Register a delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(partner: DeliveryPartnerCreate):
    pass


### Login a delivery partner
@router.post("/login")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service,
):
    token = await service.login(request_form.username, request_form.password)

    return {
        "access_token": token,
        "type": "jwt",
    }


### Update the delivery partner
@router.post("/")
async def update_delivery_partner(
    partner_update: DeliveryPartnerUPdate,
    partner: CurrentPartnerDep,
    service,
):
    pass


### Logout a delivery patner
@router.post("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(verify_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out. See you again!"}
