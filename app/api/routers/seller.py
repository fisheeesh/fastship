from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...database.redis import add_jti_to_blacklist

from ...utils import decode_acces_token

from ..dependencies import (
    CurrentSellerDep,
    SellerServiceDep,
    SessionDep,
    verify_seller_access_token,
)
from ..schemas.seller import SellerCreate, SellerRead, SellerUpdate
from ...database.models import Seller
from ...core.security import oauth2_scheme_seller

router = APIRouter(prefix="/seller", tags=["Seller"])


### Get a seller info
@router.get("/", response_model=SellerRead)
async def get_seller(
    id: UUID,
    current_seller: CurrentSellerDep,
    service: SellerServiceDep,
):
    seller = await service._get(id)

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller not found.",
        )

    if seller.id != current_seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this seller.",
        )

    return seller


### Register a seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Login the seller
@router.post("/login")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.login(request_form.username, request_form.password)

    return {
        "access_token": token,
        "type": "jwt",
    }


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
    await add_jti_to_blacklist(token_data["jti"])

    return {"details": "Successfully logged out as seller. See you again!"}


@router.get("/auth-check", response_model=SellerRead)
async def auth_check(
    token: Annotated[str, Depends(oauth2_scheme_seller)], session: SessionDep
):
    data = decode_acces_token(token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalide access token.",
        )

    user = data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token payload.",
        )

    seller = await session.get(Seller, user["id"])
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found.",
        )

    return seller


@router.patch("/")
async def update_seller(
    id: UUID,
    seller_update: SellerUpdate,
    current_seller: CurrentSellerDep,
    service: SellerServiceDep,
):
    seller = await service._get(id)

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller not found.",
        )

    if seller.id != current_seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this seller.",
        )

    update = seller_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No data provided to update.",
        )

    # if seller_update.name is not None:
    #     seller.name = seller_update.name
    # if seller_update.address is not None:
    #     seller.address = seller_update.address
    # if seller_update.zip_code is not None:
    #     seller.zip_code = seller_update.zip_code

    # return await service._update(seller)  # type: ignore
    return await service._update(current_seller.sqlmodel_update(update))
