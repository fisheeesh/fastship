from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...database.redis import add_jti_to_blacklist
from ..dependencies import (
    CurrentPartnerDep,
    PartnerServiceDep,
    verify_partner_access_token,
)
from ..schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUPdate,
)


router = APIRouter(prefix="/partner", tags=["Delivery Partner"])


### Register a delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    partner: DeliveryPartnerCreate, service: PartnerServiceDep
):
    return await service.add(partner)


### Verify a delivery partner email
@router.get("/verify")
async def verify_partner_email(
    token: str,
    service: PartnerServiceDep,
):
    await service.verify_email(token)

    return {"detail": "Your delivery partner account is verified!"}


### Login a delivery partner
@router.post("/login")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDep,
):
    token = await service.login(request_form.username, request_form.password)

    return {
        "access_token": token,
        "type": "jwt",
    }


### Update the delivery partner
@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUPdate,
    partner: CurrentPartnerDep,
    service: PartnerServiceDep,
):
    # ? Make sure to exclude none fields
    update = partner_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update.",
        )
    return await service.update(
        partner.sqlmodel_update(update),
    )


### Logout a delivery patner
@router.post("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(verify_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out as delivery partner. See you again!"}
