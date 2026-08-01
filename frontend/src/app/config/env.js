const env = {
  appName: import.meta.env.VITE_APP_NAME,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  debug: import.meta.env.VITE_DEBUG === 'true',
};

export default env;