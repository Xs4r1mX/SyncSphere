import { LogOut } from 'lucide-react';

import { useAuth } from '@/features/auth';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';

function getInitials(user) {
  if (!user) return '?';

  const name = user.display_name || `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim();
  if (name) {
    return name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? '')
      .join('');
  }

  return user.email?.[0]?.toUpperCase() ?? '?';
}

function getDisplayName(user) {
  if (!user) return 'Account';

  return (
    user.display_name ||
    `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim() ||
    user.email
  );
}

function ProfileAvatar({ user, displayName, className }) {
  return (
    <Avatar className={className}>
      {user?.profile_picture ? (
        <AvatarImage src={user.profile_picture} alt={displayName} />
      ) : null}
      <AvatarFallback>{getInitials(user)}</AvatarFallback>
    </Avatar>
  );
}

export function SidebarProfile() {
  const { user, logout } = useAuth();
  const { state } = useSidebar();
  const isCollapsed = state === 'collapsed';
  const displayName = getDisplayName(user);

  if (isCollapsed) {
    return (
      <SidebarMenu>
        <SidebarMenuItem className="group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:justify-center">
          <SidebarMenuButton
            tooltip={displayName}
            onClick={() => logout()}
            className="group-data-[collapsible=icon]:size-8! group-data-[collapsible=icon]:w-8! group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:gap-0 group-data-[collapsible=icon]:p-2!"
          >
            <ProfileAvatar
              user={user}
              displayName={displayName}
              className="size-6 shrink-0 [&_[data-slot=avatar-fallback]]:text-xs"
            />
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card/60 p-3">
      <div className="flex items-center gap-3">
        <ProfileAvatar user={user} displayName={displayName} className="size-8 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{displayName}</p>
          <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
        </div>
      </div>
      <Button variant="outline" size="sm" className="mt-3 w-full" onClick={() => logout()}>
        <LogOut />
        Log out
      </Button>
    </div>
  );
}
