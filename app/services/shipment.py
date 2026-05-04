from datetime import datetime, timedelta
from typing import cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from ..database.models import (
    DeliveryPartner,
    Review,
    Seller,
    Shipment,
    ShipmentStatus,
    TagName,
)
from ..database.redis import get_shipment_verification_code
from ..utils import decode_url_safe_token
from .base import BaseService
from .delivery_partner import DeliveryPartnerService
from .shipment_event import ShipmentEventService


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)  # type: ignore
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment:
        shipment = await self._get(id)

        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment with given id does not exist.",
            )

        return shipment

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            # seller=Seller,
        )
        # * Assign delivery partner to the shipment
        partner = await self.partner_service.assign_shipment(new_shipment)
        # * Add the delivery partner foregin key
        new_shipment.delivery_partner_id = partner.id

        shipment = cast(Shipment, await self._add(new_shipment))

        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name}.",
        )

        shipment.timeline.append(event)

        return shipment

    async def update(
        self,
        id: UUID,
        shipment_update: ShipmentUpdate,
        partner: DeliveryPartner,
    ) -> Shipment:

        # ? Validate logged in partner with assigned partner
        # ? on the shipment with given id
        shipment = await self.get(id)

        if shipment.status == ShipmentStatus.delivered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This shipment is already delivered. You cannot edit it.",
            )

        if shipment.status == ShipmentStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You cannot edit to cancelled shipment.",
            )

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        # ? Verify that the clinet is actaul client or not
        if shipment_update.status == ShipmentStatus.delivered:
            code = await get_shipment_verification_code(shipment.id)

            if code != shipment_update.verification_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Client not authorized.",
                )

        if shipment_update.estimated_delivery is not None:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        # ? Make sure to exclude none fields
        update = shipment_update.model_dump(
            exclude_none=True,
            exclude=["verification_code"],  # type: ignore
        )
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided to update.",
            )

        if len(update) > 1 or not shipment_update.estimated_delivery:
            await self.event_service.add(
                shipment=shipment,
                **update,
            )

        return cast(Shipment, await self._update(shipment))

    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        # * Validate the seller
        shipment = await self.get(id)

        if shipment.status == ShipmentStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="This shipment is already cancelled.",
            )

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )
        shipment.timeline.append(event)
        shipment.estimated_delivery = None

        return cast(Shipment, await self._update(shipment))

    async def delete(self, id: UUID, seller: Seller) -> None:
        shipment = await self.get(id)

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized.",
            )

        try:
            await self.event_service.delete_by_shipment(shipment.id)
            await self._delete(shipment)
        except Exception:
            await self.session.rollback()
            raise

    async def rate(self, token: str, rating: int, comment: str | None):
        token_data = decode_url_safe_token(token)

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )

        shipment = await self.get(UUID(token_data["id"]))  # type: ignore

        new_review = Review(
            rating=rating,
            comment=comment if comment else None,
            shipment_id=shipment.id,
        )  # type: ignore

        self.session.add(new_review)
        await self.session.commit()

    async def add_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        tag = await tag_name.tag(self.session)

        if tag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found.",
            )

        if any(existing_tag.id == tag.id for existing_tag in shipment.tags):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists on shipment.",
            )

        shipment.tags.append(tag)

        return await self._update(shipment)

    async def remove_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        tag = await tag_name.tag(self.session)

        if tag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found.",
            )

        try:
            shipment.tags.remove(tag)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag doesn't exist on shipment.",
            )

        return await self._update(shipment)
