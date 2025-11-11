from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services.seller import SellerService
from app.services.shipment import ShipmentService

# * Asynchronous database session dependency nnotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# * Shipment service dependency
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)


# * Seller service dependency
def get_seller_service(session: SessionDep):
    return SellerService(session)


# * Shipment service dependency annotation
ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

# * Seller service dependency annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]
