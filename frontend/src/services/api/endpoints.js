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
    connectionEnable: (uuid) => `/cloud/connections/${uuid}/enable/`,
    connectionUnlink: (uuid) => `/cloud/connections/${uuid}/unlink/`,
    connectionHealth: (uuid) => `/cloud/connections/${uuid}/health/`,
    providerAuthorize: (provider) => `/cloud/providers/${provider}/authorize/`,
    providerCallback: (provider) => `/cloud/providers/${provider}/callback/`,
  },
  files: {
    list: (uuid) => `/files/${uuid}/`,
    quota: (uuid) => `/files/${uuid}/quota/`,
    breadcrumb: (uuid) => `/files/${uuid}/breadcrumb/`,
    folders: (uuid) => `/files/${uuid}/folders/`,
    upload: (uuid) => `/files/${uuid}/upload/`,
    item: (uuid, itemId) => `/files/${uuid}/${encodeURIComponent(itemId)}/`,
    download: (uuid, itemId) =>
      `/files/${uuid}/${encodeURIComponent(itemId)}/download/`,
    copy: (uuid, itemId) => `/files/${uuid}/${encodeURIComponent(itemId)}/copy/`,
    restore: (uuid, itemId) =>
      `/files/${uuid}/${encodeURIComponent(itemId)}/restore/`,
  },
  transfers: {
    list: '/transfers/',
    job: (uuid) => `/transfers/${uuid}/`,
    items: (uuid) => `/transfers/${uuid}/items/`,
    cancel: (uuid) => `/transfers/${uuid}/cancel/`,
  },
};

export default endpoints;
