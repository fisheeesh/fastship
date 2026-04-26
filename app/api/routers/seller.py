from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...database.redis import add_jti_to_blacklist

from ...utils import decode_acces_token

from ..dependencies import SellerServiceDep, SessionDep, verify_access_token
from ..schemas.seller import SellerCreate, SellerRead
from ...database.models import Seller
from ...core.security import oauth2_scheme

router = APIRouter(prefix="/seller", tags=["Seller"])


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


### Logout the seller
@router.get("/logout")
async def logout_seller(
    token_data: Annotated[dict, Depends(verify_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    
    return {
        "details": "Successfully logged out. See you again!"
    }


@router.get("/auth-check", response_model=SellerRead)
async def auth_check(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
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
