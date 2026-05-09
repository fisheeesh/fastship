import { useQuery } from "@tanstack/react-query"
import { useContext } from "react"
import { Link, Navigate } from "react-router"
import { AppSidebar } from "~/components/app-sidebar"
import ShipmentCard from "~/components/shipment-card"
import { Button } from "~/components/ui/button"
import Loading from "~/components/ui/loading"
import { Separator } from "~/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "~/components/ui/sidebar"
import { AuthContext } from "~/contexts/auth-context"
import api from "~/lib/api"
import { ShipmentStatus } from "~/lib/client"
import { getShipmentCountWithStatus } from "~/lib/utils"

export default function DashboardPage() {
  const { token, user } = useContext(AuthContext)
  if (!token) {
    return (
      <Navigate to="/" />
    )
  }

  const { data, isPending, isError } = useQuery({
    queryKey: ['shipments'],
    queryFn: async () => {
      const shipmentsApi = user === 'seller' ? api.seller.getShipments() : api.partner.getShipments()

      const { data } = await shipmentsApi

      return data
    }
  })

  if (isError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-2">
        <h1 className="text-red-600 font-bold text-4xl">Error loading shipments</h1>
        <Button type="button" className="min-h-11" asChild>
          <Link to="/dashboard">
            Go Back to Dashboard
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "19rem",
        } as React.CSSProperties
      }
    >
      <AppSidebar currentRoute="Dashboard" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator
            orientation="vertical"
            className="mr-2 data-vertical:h-4 data-vertical:self-auto"
          />
          <h2>Dashboard</h2>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {
            isPending || !data ? <Loading /> : (
              <>
                <div className="grid auto-rows-min gap-4 md:grid-cols-4">
                  <NumberLabel value={data?.length} label="Total Shipments" />
                  <NumberLabel value={getShipmentCountWithStatus(data, ShipmentStatus.Placed)} label="Placed" />
                  <NumberLabel value={getShipmentCountWithStatus(data, ShipmentStatus.InTransit)} label="In Transit" />
                  <NumberLabel value={getShipmentCountWithStatus(data, ShipmentStatus.Delivered)} label="Delivered" />
                </div>
                <div className="grid auto-rows-min gap-4 md:grid-cols-4">
                  {
                    data.map(shipment => (
                      <ShipmentCard
                        shipment={shipment}
                        key={shipment.id}
                      />
                    ))
                  }
                </div>
              </>
            )
          }

        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

function NumberLabel({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-gray-200 p-4">
      <h1 className="text-4xl font-bold">{value}</h1>
      <p className="text-gray-500">{label}</p>
    </div>
  )
}
