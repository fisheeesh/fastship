from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import Shipment, ShipmentEvent, ShipmentStatus
from .base import BaseService


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(ShipmentEvent, session)  # type: ignore

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

        return await self._add(new_event)  # type: ignore

    async def get_latest_event(self, shipment: Shipment):
        timeline = shipment.timeline

        timeline.sort(key=lambda event: event.created_at)

        return timeline[-1]

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
