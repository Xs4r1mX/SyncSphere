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
};

export default endpoints;
