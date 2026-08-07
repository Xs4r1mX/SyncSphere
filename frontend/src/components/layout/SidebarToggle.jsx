import { PanelLeft, PanelLeftClose } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';

export function SidebarToggle({ collapsedOnly = false }) {
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === 'collapsed';

  if (isCollapsed || collapsedOnly) {
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            tooltip="Expand sidebar"
            onClick={toggleSidebar}
            aria-label="Expand sidebar"
          >
            <PanelLeft />
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    );
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      onClick={toggleSidebar}
      aria-label="Collapse sidebar"
      className="shrink-0 text-muted-foreground hover:text-foreground"
    >
      <PanelLeftClose className="size-4" />
    </Button>
  );
}
