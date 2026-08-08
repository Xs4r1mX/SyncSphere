const endpoints = {
  auth: {
    login: '/iam/auth/login/',
    register: '/iam/auth/register/',
    logout: '/iam/auth/logout/',
    refresh: '/iam/auth/refresh/',
    me: '/iam/auth/me/',
    forgotPassword: '/iam/auth/forgot-password/',
    resetPassword: '/iam/auth/reset-password/',
    changePassword: '/iam/auth/change-password/',
    verifyEmail: (token) => `/iam/auth/verify-email/${token}/`,
    resendVerification: '/iam/auth/resend-verification/',
  },
  cloud: {
    connections: '/cloud/connections/',
    connection: (uuid) => `/cloud/connections/${uuid}/`,
    connectionDisable: (uuid) => `/cloud/connections/${uuid}/disable/`,
    connectionUnlink: (uuid) => `/cloud/connections/${uuid}/unlink/`,
    connectionHealth: (uuid) => `/cloud/connections/${uuid}/health/`,
    providerAuthorize: (provider) => `/cloud/providers/${provider}/authorize/`,
    providerCallback: (provider) => `/cloud/providers/${provider}/callback/`,
  },
};

export default endpoints;
