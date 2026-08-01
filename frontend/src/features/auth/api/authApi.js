import authService from '../services/authService';
import { AppError, normalizeApiError } from '@/services/api/error';

async function unwrap(request) {
  try {
    const response = await request;
    const body = response.data;

    if (body && typeof body.success === 'boolean' && body.success === false) {
      throw new AppError(body.message || 'Request failed.', {
        status: response.status,
        fieldErrors: body.errors,
        data: body.data,
      });
    }

    if (body && typeof body.success === 'boolean') {
      return body.data;
    }

    return body;
  } catch (error) {
    throw normalizeApiError(error);
  }
}

export const login = (payload) => unwrap(authService.login(payload));

export const register = (payload) => unwrap(authService.register(payload));

export const logout = (payload) => unwrap(authService.logout(payload));

export const refresh = (payload) => unwrap(authService.refresh(payload));

export const me = () => unwrap(authService.me());

export const forgotPassword = (payload) =>
  unwrap(authService.forgotPassword(payload));

export const resetPassword = (payload) =>
  unwrap(authService.resetPassword(payload));

export const changePassword = (payload) =>
  unwrap(authService.changePassword(payload));

export const verifyEmail = (token) => unwrap(authService.verifyEmail(token));

export const resendVerification = (payload) =>
  unwrap(authService.resendVerification(payload));

const authApi = {
  login,
  register,
  logout,
  refresh,
  me,
  forgotPassword,
  resetPassword,
  changePassword,
  verifyEmail,
  resendVerification,
};

export default authApi;
