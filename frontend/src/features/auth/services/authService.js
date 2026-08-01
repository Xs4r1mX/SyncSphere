import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const authService = {
  login(credentials) {
    return api.post(endpoints.auth.login, credentials);
  },

  register(payload) {
    return api.post(endpoints.auth.register, payload);
  },

  logout(payload) {
    return api.post(endpoints.auth.logout, payload, {
      _skipAuthRefresh: true,
    });
  },

  refresh(payload) {
    return api.post(endpoints.auth.refresh, payload, {
      _skipAuthRefresh: true,
    });
  },

  me() {
    return api.get(endpoints.auth.me);
  },

  forgotPassword(payload) {
    return api.post(endpoints.auth.forgotPassword, payload);
  },

  resetPassword(payload) {
    return api.post(endpoints.auth.resetPassword, payload);
  },

  changePassword(payload) {
    return api.post(endpoints.auth.changePassword, payload);
  },

  verifyEmail(token) {
    return api.get(endpoints.auth.verifyEmail(token));
  },

  resendVerification(payload) {
    return api.post(endpoints.auth.resendVerification, payload);
  },
};

export default authService;
