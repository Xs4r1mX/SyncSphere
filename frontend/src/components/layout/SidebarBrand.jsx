import { Link } from 'react-router-dom';

import { SidebarToggle } from './SidebarToggle';
import env from '@/app/config/env';
import { PATHS } from '@/app/routes/paths';
import { useSidebar } from '@/components/ui/sidebar';

const LOGO_ICON_SRC = '/sync_sphere%20_logo_only.png';

export function SidebarBrand() {
  const { state } = useSidebar();
  const isCollapsed = state === 'collapsed';

  if (isCollapsed) {
    return <SidebarToggle collapsedOnly />;
  }

  return (
    <div className="flex h-8 w-full items-center gap-2">
      <Link
        to={PATHS.DASHBOARD}
        className="flex min-w-0 flex-1 items-center gap-2 overflow-hidden rounded-md"
        aria-label={env.appName}
      >
        <img
          src={LOGO_ICON_SRC}
          alt=""
          aria-hidden
          className="size-8 shrink-0 object-contain"
        />
        <span className="truncate text-sm font-semibold">{env.appName}</span>
      </Link>
      <SidebarToggle />
    </div>
  );
}
