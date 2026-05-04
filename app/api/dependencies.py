from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import oauth2_scheme_partner, oauth2_scheme_seller
from ..database.models import DeliveryPartner, Seller
from ..database.redis import is_jti_blacklisted
from ..database.session import get_session
from ..services.delivery_partner import DeliveryPartnerService
from ..services.seller import SellerService
from ..services.shipment import ShipmentService
from ..services.shipment_event import ShipmentEventService
from ..utils import decode_acces_token

# $ Annotated -> [type, bl ka ya ll]

# * Asyn database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# * Verify access token dep
async def _verify_access_token(
    token: str,
) -> dict:
    data = decode_acces_token(token)

    # * Validate the token
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    return data


### Seller access token data
async def verify_seller_access_token(
    token: Annotated[str, Depends(oauth2_scheme_seller)],
):
    return await _verify_access_token(token)


### Delivery Partner access token data
async def verify_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
):
    return await _verify_access_token(token)


# * Current Seller
async def get_current_seller(
    token_data: Annotated[dict, Depends(verify_seller_access_token)],
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


# * Current Seller
async def get_current_partner(
    token_data: Annotated[dict, Depends(verify_partner_access_token)],
    session: SessionDep,
):
    user = token_data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or access token payload.",
        )

    partner = await session.get(DeliveryPartner, UUID(user["id"]))
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    return partner


# * Shipment service dep
def get_shipment_service(session: SessionDep):
    return ShipmentService(
        session,
        DeliveryPartnerService(session),
        ShipmentEventService(session),
    )


# * Seller service dep
def get_seller_service(session: SessionDep):
    return SellerService(session)


# * Delivery partner service dep
def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerService(session)


# * Current Seller Dep
CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]

# * Current Partner Dep
CurrentPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]


# * Shipment service dep annotation
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

# * Seller service dep annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

# * Delivery partner service dep annotation
PartnerServiceDep = Annotated[
    DeliveryPartnerService,
    Depends(get_delivery_partner_service),
]
