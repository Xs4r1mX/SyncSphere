import { Outlet } from 'react-router-dom';

import { AppSidebar } from '@/components/layout/AppSidebar';
import { PageBackgroundOverlay } from '@/components/layout/PageBackground';
import { getSidebarDefaultOpen } from '@/components/layout/sidebarState';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';

export function DashboardLayout() {
  return (
    <SidebarProvider defaultOpen={getSidebarDefaultOpen()} className="min-h-svh w-full">
      <AppSidebar />
      <SidebarInset className="relative min-h-svh min-w-0 flex-1 flex-col overflow-x-hidden">
        <PageBackgroundOverlay />
        <div className="relative flex min-h-svh w-full min-w-0 flex-1 flex-col">
          <div className="flex shrink-0 items-center px-4 py-3 md:hidden">
            <SidebarTrigger className="-ml-1" />
          </div>
          <div className="w-full min-w-0 flex-1 p-4 md:p-6 lg:p-8">
            <Outlet />
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
