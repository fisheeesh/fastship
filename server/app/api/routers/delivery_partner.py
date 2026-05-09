from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from app.api.schemas.shipment import ShipmentRead
from app.api.tag import APITag
from app.core.security import TokenData
from app.utils import TEMPLATE_DIR

from app.config import app_settings
from app.core.exceptions import NothingToUpdate

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

router = APIRouter(prefix="/partner", tags=[APITag.PARTNER])


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
@router.post("/login", response_model=TokenData)
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDep,
):
    token = await service.login(request_form.username, request_form.password)

    return {
        "access_token": token,
        "token_type": "bearer",
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
        raise NothingToUpdate("No data provided to update.")
    return await service.update(
        partner.sqlmodel_update(update),
    )


### Logout a delivery patner
@router.post("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(verify_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])  # type: ignore
    return {"detail": "Successfully logged out as delivery partner. See you again!"}


### Forgot password link
@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    service: PartnerServiceDep,
):
    await service.send_password_reset_link(email, router.prefix)

    return {"detail": "Check email for password reset link."}


### Reset password form
@router.get("/reset-password-form")
async def get_reset_password_form(
    request: Request,
    token: str,
):
    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        context={
            "reset_url": f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset-password?token={token}"
        },
        name="password/reset.html",
    )


### Reset password
@router.post("/reset-password")
async def reset_password(
    request: Request,
    token: str,
    password: str,
    service: PartnerServiceDep,
):
    is_success = await service.reset_password(token, password)

    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="password/reset_success.html"
        if is_success
        else "password/reset_failed.html",
    )


## Get all shipments assigned to the delivery partner
@router.get("/shipments", response_model=list[ShipmentRead])
async def get_shipments(partner: CurrentPartnerDep):
    return partner.shipments
