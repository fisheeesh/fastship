from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.redis import is_jti_blacklisted

from ..database.models import Seller
from ..utils import decode_acces_token

from ..services.seller import SellerService

from ..database.session import get_session
from ..services.shipment import ShipmentService
from ..core.security import oauth2_scheme

# $ Annotated -> [type, bl ka ya ll]

# * Asyn database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# * Verify access token dep
async def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    data = decode_acces_token(token)

    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    return data


# * Current Seller
async def get_current_seller(
    token_data: Annotated[dict, Depends(verify_access_token)],
    session: SessionDep,
):
    user = token_data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or access token payload.",
        )

    seller = await session.get(Seller, UUID(user["id"]))
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )

    return seller


# * Shipment service dep
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)


# * Seller service dep
def get_seller_service(session: SessionDep):
    return SellerService(session)


# * Current Seller Dep
CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]


# * Shipment service dep annotation
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

# * Seller service dep annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]
