import * as React from "react"

import { GalleryVerticalEndIcon } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from "~/components/ui/sidebar"
import { AuthContext } from "~/contexts/auth-context"
import { Link } from "react-router"

const menuItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
  },
  {
    title: "Account",
    url: "/account"
  }
]


export function AppSidebar({ currentRoute, ...props }: { currentRoute: string } & React.ComponentProps<typeof Sidebar>) {
  const { user } = React.useContext(AuthContext)

  return (
    <Sidebar variant="floating" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <GalleryVerticalEndIcon className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-medium">Documentation</span>
                  <span className="">v1.0.0</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu className="gap-1">
            {menuItems.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton asChild isActive={currentRoute == item.title}>
                  <Link to={item.url}>
                    {item.title}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
            {
              user === 'seller' && (
                <SidebarMenuItem>
                  <SidebarMenuButton asChild isActive={currentRoute == 'submit-shipment'}>
                    <Link to="/submit-shipment">
                      Submit Shipment
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              )
            }
            {
              user === 'partner' && (
                <SidebarMenuItem>
                  <SidebarMenuButton asChild isActive={currentRoute == 'submit-shipment'}>
                    <Link to="/update-shipment">
                      Update Shipment
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              )
            }
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar >
  )
}
