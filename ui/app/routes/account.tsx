import { useQuery } from "@tanstack/react-query"
import { useContext } from "react"
import { Link, Navigate } from "react-router"
import { AppSidebar } from "~/components/app-sidebar"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import Loading from "~/components/ui/loading"
import { Separator } from "~/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "~/components/ui/sidebar"
import { AuthContext } from "~/contexts/auth-context"
import api from "~/lib/api"

export default function AccountPage() {
  const { token, user, logout } = useContext(AuthContext)

  if (!token) {
    return (
      <Navigate to="/" />
    )
  }

  const { data, isPending, isError } = useQuery({
    queryKey: ['account'],
    queryFn: async () => {
      const profileApi = user === 'seller' ? api.seller.getSellerProfile() : api.partner.getPartnerProfile()

      const { data } = await profileApi

      return data
    }
  })

  if (isError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-2">
        <h1 className="text-red-600 font-bold text-4xl">Error loading account details</h1>
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
      <AppSidebar currentRoute="Account" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator
            orientation="vertical"
            className="mr-2 data-vertical:h-4 data-vertical:self-auto"
          />
          <h2>Account Details</h2>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {
            isPending || !data ? <Loading /> : (
              <div className="flex flex-col gap-4 max-w-100">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={data?.name ?? "..."}
                  readOnly
                  className="min-h-11"
                />
                <Label htmlFor="email">Name</Label>
                <Input
                  id="email"
                  value={data?.email ?? "..."}
                  readOnly
                  className="min-h-11"
                />
                <Button
                  type="button"
                  variant="destructive"
                  onClick={logout}
                  className="w-min ml-auto min-h-11"
                >
                  Logout
                </Button>
              </div>
            )
          }

        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
