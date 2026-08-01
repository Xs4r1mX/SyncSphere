import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import authApi from '../api/authApi';
import { logout as logoutAction } from '../store/authSlice';
import { PATHS } from '@/app/routes/paths';
import tokenService from '@/services/storage/tokenService';

export function useAuth() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);

  const logout = useCallback(async () => {
    const refresh = tokenService.getRefreshToken();

    try {
      if (refresh) {
        await authApi.logout({ refresh });
      }
    } catch {
      // Always clear local session even if blacklist fails.
    } finally {
      tokenService.clearTokens();
      dispatch(logoutAction());
      navigate(PATHS.LOGIN, { replace: true });
    }
  }, [dispatch, navigate]);

  return {
    ...auth,
    logout,
  };
}
