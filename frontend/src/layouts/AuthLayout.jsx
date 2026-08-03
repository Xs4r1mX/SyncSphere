import { Outlet } from 'react-router-dom';

import { Logo } from '@/components/Logo';

export function AuthLayout() {
  return (
    <div className="relative min-h-svh overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_oklch(0.22_0_0)_0%,_transparent_55%),linear-gradient(180deg,_oklch(0.14_0_0),_oklch(0.10_0_0))]" />
      <div className="relative mx-auto flex min-h-svh w-full flex-col items-center justify-center px-4 pb-32 pt-6">
        <Logo size="lg" className="-mb-14 h-64 w-auto max-w-[min(720px,100%)]" />
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
