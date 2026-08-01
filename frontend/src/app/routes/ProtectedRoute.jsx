import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { PATHS } from './paths';

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, status } = useSelector((state) => state.auth);

  if (status === 'loading' || status === 'idle') {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
        Loading session…
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate to={PATHS.LOGIN} replace state={{ from: location.pathname }} />
    );
  }

  return <Outlet />;
}
