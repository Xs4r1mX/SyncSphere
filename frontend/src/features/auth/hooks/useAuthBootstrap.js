import { useEffect } from 'react';
import { useDispatch } from 'react-redux';

import authApi from '../api/authApi';
import {
  setCredentials,
  setLoading,
  setUnauthenticated,
} from '../store/authSlice';
import tokenService from '@/services/storage/tokenService';

export function useAuthBootstrap() {
  const dispatch = useDispatch();

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      dispatch(setLoading());

      try {
        if (tokenService.hasAccessToken()) {
          const user = await authApi.me();
          if (!cancelled) {
            dispatch(setCredentials(user));
          }
          return;
        }

        if (tokenService.hasRefreshToken()) {
          const tokens = await authApi.refresh({
            refresh: tokenService.getRefreshToken(),
          });

          tokenService.setTokens({
            access: tokens.access,
            refresh: tokens.refresh,
          });

          const user = await authApi.me();
          if (!cancelled) {
            dispatch(setCredentials(user));
          }
          return;
        }

        if (!cancelled) {
          dispatch(setUnauthenticated());
        }
      } catch {
        tokenService.clearTokens();
        if (!cancelled) {
          dispatch(setUnauthenticated());
        }
      }
    }

    bootstrap();

    return () => {
      cancelled = true;
    };
  }, [dispatch]);
}
