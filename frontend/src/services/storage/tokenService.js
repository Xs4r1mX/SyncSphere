const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

const tokenService = {
  getAccessToken() {
    return localStorage.getItem(ACCESS_KEY);
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  },

  setTokens({ access, refresh }) {
    if (access) {
      localStorage.setItem(ACCESS_KEY, access);
    }
    if (refresh) {
      localStorage.setItem(REFRESH_KEY, refresh);
    }
  },

  clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },

  hasAccessToken() {
    return Boolean(localStorage.getItem(ACCESS_KEY));
  },

  hasRefreshToken() {
    return Boolean(localStorage.getItem(REFRESH_KEY));
  },
};

export default tokenService;
