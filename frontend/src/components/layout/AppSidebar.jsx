import { Link, useLocation } from 'react-router-dom';
import { LogOut } from 'lucide-react';

import { FOOTER_NAV_ITEMS, MAIN_NAV_ITEMS } from './navConfig';
import { SidebarBrand } from './SidebarBrand';
import { SidebarProfile } from './SidebarProfile';
import { sidebarInsetX } from './sidebarPadding';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';

function NavItems({ items }) {
  const location = useLocation();

  return (
    <SidebarMenu>
      {items.map((item) => {
        const isActive = location.pathname === item.path;
        const Icon = item.icon;

        return (
          <SidebarMenuItem key={item.path}>
            <SidebarMenuButton
              render={<Link to={item.path} />}
              isActive={isActive}
              tooltip={item.label}
            >
              <Icon />
              <span>{item.label}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        );
      })}
    </SidebarMenu>
  );
}

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="gap-0 p-0">
        <SidebarGroup className={cn(sidebarInsetX, 'pt-4 pb-4')}>
          <SidebarGroupContent>
            <SidebarBrand />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarHeader>

      <SidebarContent className="pt-0">
        <SidebarGroup className={cn(sidebarInsetX, 'pt-0 pb-2')}>
          <SidebarGroupContent>
            <NavItems items={MAIN_NAV_ITEMS} />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="mt-auto gap-0 p-0">
        <SidebarGroup className={cn(sidebarInsetX, 'py-2')}>
          <SidebarGroupContent>
            <NavItems items={FOOTER_NAV_ITEMS} />
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup className={cn(sidebarInsetX, 'pb-4')}>
          <SidebarGroupContent>
            <SidebarProfile />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarFooter>
    </Sidebar>
  );
}
