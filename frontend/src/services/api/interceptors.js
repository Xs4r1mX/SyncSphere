import api from './axios';
import endpoints from './endpoints';
import tokenService from '@/services/storage/tokenService';
import { store } from '@/app/store';
import { setUnauthenticated } from '@/features/auth/store/authSlice';
import { PATHS } from '@/app/routes/paths';

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token);
    }
  });
  failedQueue = [];
}

function shouldSkipRefresh(url = '') {
  return (
    url.includes('/iam/auth/login') ||
    url.includes('/iam/auth/register') ||
    url.includes('/iam/auth/refresh') ||
    url.includes('/iam/auth/forgot-password') ||
    url.includes('/iam/auth/reset-password') ||
    url.includes('/iam/auth/verify-email') ||
    url.includes('/iam/auth/resend-verification') ||
    url.includes('/iam/auth/logout')
  );
}

function forceLogout() {
  tokenService.clearTokens();
  store.dispatch(setUnauthenticated());

  if (window.location.pathname !== PATHS.LOGIN) {
    window.location.assign(PATHS.LOGIN);
  }
}

export function setupInterceptors() {
  api.interceptors.request.use(
    (config) => {
      const token = tokenService.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (!originalRequest || error.response?.status !== 401) {
        return Promise.reject(error);
      }

      if (
        originalRequest._retry ||
        originalRequest._skipAuthRefresh ||
        shouldSkipRefresh(originalRequest.url)
      ) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = tokenService.getRefreshToken();

      if (!refreshToken) {
        isRefreshing = false;
        forceLogout();
        return Promise.reject(error);
      }

      try {
        const { data } = await api.post(
          endpoints.auth.refresh,
          { refresh: refreshToken },
          { _skipAuthRefresh: true }
        );

        const tokens = data?.data;
        if (!tokens?.access || !tokens?.refresh) {
          throw new Error('Invalid refresh response');
        }

        tokenService.setTokens({
          access: tokens.access,
          refresh: tokens.refresh,
        });

        processQueue(null, tokens.access);
        originalRequest.headers.Authorization = `Bearer ${tokens.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        forceLogout();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
  );
}

setupInterceptors();
