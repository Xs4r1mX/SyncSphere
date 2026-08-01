import { Outlet } from 'react-router-dom';

import env from '@/app/config/env';

export function AuthLayout() {
  return (
    <div className="relative min-h-svh overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_oklch(0.92_0.03_250),_transparent_55%),linear-gradient(180deg,_oklch(0.98_0.01_240),_oklch(0.96_0.02_220))]" />
      <div className="relative mx-auto flex min-h-svh w-full max-w-md flex-col justify-center gap-8 px-4 py-10">
        <div className="text-center">
          <p className="text-2xl font-semibold tracking-tight">{env.appName}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Central cloud storage management
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
