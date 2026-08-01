import { Link, Outlet } from 'react-router-dom';

import { useAuth } from '@/features/auth';
import { PATHS } from '@/app/routes/paths';
import env from '@/app/config/env';
import { Button } from '@/components/ui/button';

export function DashboardLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-svh bg-background">
      <header className="border-b">
        <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Link to={PATHS.DASHBOARD} className="font-semibold tracking-tight">
              {env.appName}
            </Link>
            <nav className="flex items-center gap-4 text-sm text-muted-foreground">
              <Link
                to={PATHS.DASHBOARD}
                className="hover:text-foreground"
              >
                Dashboard
              </Link>
              <Link
                to={PATHS.SETTINGS}
                className="hover:text-foreground"
              >
                Settings
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-muted-foreground sm:inline">
              {user?.email}
            </span>
            <Button variant="outline" size="sm" onClick={() => logout()}>
              Log out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
