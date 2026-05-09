import { useContext } from "react"
import { Navigate } from "react-router"
import { AppSidebar } from "~/components/app-sidebar"
import { SubmitShipmentForm } from "~/components/submit-shipment-form"
import { Separator } from "~/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "~/components/ui/sidebar"
import { AuthContext } from "~/contexts/auth-context"

export default function SubmitShipmentPage() {
  const { token, user, logout } = useContext(AuthContext)

  if (!token || user !== "seller") {
    return (
      <Navigate to="/" />
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
      <AppSidebar currentRoute="submit-shipment" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator
            orientation="vertical"
            className="mr-2 data-vertical:h-4 data-vertical:self-auto"
          />
          <h2>Submit Shipment</h2>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0 max-w-150">
          <SubmitShipmentForm />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
