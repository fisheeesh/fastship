from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.api.tag import APITag
from app.config import app_settings
from app.core.exceptions import (
    ClientNotAuthorized,
    EntityNotFound,
    InvalidToken,
    NothingToUpdate,
)

from ...core.security import TokenData, oauth2_scheme_seller
from ...database.models import Seller
from ...database.redis import add_jti_to_blacklist
from ...utils import TEMPLATE_DIR, decode_acces_token
from ..dependencies import (
    CurrentSellerDep,
    SellerServiceDep,
    SessionDep,
    verify_seller_access_token,
)
from ..schemas.seller import SellerCreate, SellerRead, SellerUpdate

router = APIRouter(prefix="/seller", tags=[APITag.SELLER])


### Get a seller info
@router.get("/", response_model=SellerRead)
async def get_seller(
    id: UUID,
    current_seller: CurrentSellerDep,
    service: SellerServiceDep,
):
    seller = await service._get(id)

    if seller is None:
        raise EntityNotFound("Seller not found.")

    if seller.id != current_seller.id:
        raise ClientNotAuthorized("You are not allowed to update this seller.")

    return seller


### Register a seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Login the seller
@router.post("/login", response_model=TokenData)
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.login(request_form.username, request_form.password)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


### Get seller profile
@router.get("/me", response_model=SellerRead)
async def get_seller_profile(seller: SellerServiceDep):
    return seller


### Verify Seller Email
@router.get("/verify")
async def verify_serller_email(
    token: str,
    service: SellerServiceDep,
):
    await service.verify_email(token)

    return {"detail": "Your seller account is verified!"}


### Logout the seller
@router.get("/logout")
async def logout_seller(
    token_data: Annotated[dict, Depends(verify_seller_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])  # type: ignore

    return {"details": "Successfully logged out as seller. See you again!"}


@router.get("/auth-check", response_model=SellerRead)
async def auth_check(
    token: Annotated[str, Depends(oauth2_scheme_seller)], session: SessionDep
):
    data = decode_acces_token(token)

    if data is None:
        raise InvalidToken("Invalide access token.")

    user = data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise InvalidToken("Invalid access token payload.")

    seller = await session.get(Seller, user["id"])
    if seller is None:
        raise EntityNotFound("Seller not found.")

    return seller


### Update Seller Info
@router.patch("/")
async def update_seller(
    id: UUID,
    seller_update: SellerUpdate,
    current_seller: CurrentSellerDep,
    service: SellerServiceDep,
):
    seller = await service._get(id)

    if seller is None:
        raise EntityNotFound("Seller not found.")

    if seller.id != current_seller.id:
        raise ClientNotAuthorized("You are not allowed to update this seller.")

    update = seller_update.model_dump(exclude_none=True)

    if not update:
        raise NothingToUpdate("No data provided to update.")

    # if seller_update.name is not None:
    #     seller.name = seller_update.name
    # if seller_update.address is not None:
    #     seller.address = seller_update.address
    # if seller_update.zip_code is not None:
    #     seller.zip_code = seller_update.zip_code

    # return await service._update(seller)  # type: ignore
    return await service._update(current_seller.sqlmodel_update(update))


### Email Password Reset Link
@router.post("/forgot-password")
async def forgort_password(
    email: EmailStr,
    service: SellerServiceDep,
):
    await service.send_password_reset_link(email, router.prefix)

    return {"detail": "Check email for password reset link."}


### Passwrod Reset Form
@router.get("/reset-password-form")
async def get_reset_password_form(request: Request, token: str):
    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="password/reset.html",
        context={
            "reset_url": f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset-password?token={token}"
        },
    )


### Reset Seller Password
@router.post("/reset-password")
async def reset_password(
    request: Request,
    token: str,
    password: Annotated[str, Form()],
    service: SellerServiceDep,
):
    is_success = await service.reset_password(token, password)

    templates = Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="password/reset_success.html"
        if is_success
        else "password/reset_failed.html",
    )
