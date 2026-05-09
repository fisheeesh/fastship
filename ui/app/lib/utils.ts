import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { ShipmentRead } from "./client"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const getLatestStatus = (shipment: ShipmentRead) => {
  return shipment.timeline[shipment.timeline.length - 1].status
}

export const getShipmentCountWithStatus = (shipments: ShipmentRead[], status: string) => {
  return shipments.filter(shipment => getLatestStatus(shipment) === status).length
}