from random import randint
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils import generate_url_safe_token

from ..database.redis import add_shipment_verification_code

from .notification import NotificationService

from ..database.models import Shipment, ShipmentEvent, ShipmentStatus
from .base import BaseService
from app.config import app_settings


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession, tasks):
        super().__init__(ShipmentEvent, session)  # type: ignore
        self.notification_service = NotificationService(tasks)

    async def add(
        self,
        shipment: Shipment,
        location: Optional[int] = None,
        status: Optional[ShipmentStatus] = None,
        description: Optional[str] = None,
    ) -> ShipmentEvent:
        if location is None or status is None:
            last_event = await self.get_latest_event(shipment)
            location = location if location is not None else last_event.location
            status = status if status is not None else last_event.status

        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=description
            if description
            else self._generate_description(
                status,
                location,
            ),
            shipment_id=shipment.id,
        )  # type: ignore

        await self._notify(shipment, status)

        return await self._add(new_event)  # type: ignore

    async def get_latest_event(self, shipment: Shipment):
        timeline = shipment.timeline

        timeline.sort(key=lambda event: event.created_at)

        return timeline[-1]

    async def delete_by_shipment(self, shipment_id: UUID) -> None:
        await self.session.execute(
            delete(ShipmentEvent).where(ShipmentEvent.shipment_id == shipment_id)  # type: ignore
        )

    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return "cancelled by the seller"
            case _:  # * and ShipmentStatus.in_transit
                return f"scanned at {location}"

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        if status == ShipmentStatus.in_transit:
            return

        subject: str
        template_name: str
        context: dict[str, Any]

        match status:
            case ShipmentStatus.placed:
                subject = "Your Order is Shipping 🚐"
                template_name = "mail_placed.html"
                context = {
                    "id": shipment.id,
                    "seller": shipment.seller.name,
                    "partner": shipment.delivery_partner.name,
                }
            case ShipmentStatus.out_for_delivery:
                subject = "Your Order is Arriving Soon 🔜"
                template_name = "mail_out_for_delivery.html"
                context = {}

                code = randint(100_000, 999_999)
                await add_shipment_verification_code(shipment.id, code)

                if shipment.client_contact_phone:
                    await self.notification_service.send_sms(
                        to=shipment.client_contact_phone,  # type: ignore
                        body=f"Your order is arriving soon! Share the {code} code with the delivery executive to receive your package.",
                    )
                else:
                    context = {"verification_code": code}
            case ShipmentStatus.delivered:
                token = generate_url_safe_token({"id": str(shipment.id)})

                subject = "Your Order is Delivered ✅"
                template_name = "mail_delivered.html"
                context = {
                    "seller": shipment.seller.name,
                    "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review-form?token={token}",
                }
            case ShipmentStatus.cancelled:
                subject = "Your Order Was Cancelled"
                template_name = "mail_cancelled.html"
                context = {}

        await self.notification_service.send_email_with_template(
            recipients=[shipment.client_contact_email],
            subject=subject,
            context=context,
            template_name=template_name,
        )
