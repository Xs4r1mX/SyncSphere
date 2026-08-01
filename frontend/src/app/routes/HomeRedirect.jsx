import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { PATHS } from './paths';

export function HomeRedirect() {
  const { isAuthenticated, status } = useSelector((state) => state.auth);

  if (status === 'loading' || status === 'idle') {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
        Loading session…
      </div>
    );
  }

  return (
    <Navigate
      to={isAuthenticated ? PATHS.DASHBOARD : PATHS.LOGIN}
      replace
    />
  );
}
