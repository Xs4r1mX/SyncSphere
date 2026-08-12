export const PATHS = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  VERIFY_EMAIL: '/verify-email',
  DASHBOARD: '/dashboard',
  CLOUD_STORAGES: '/cloud-storages',
  CLOUD_FILES: '/cloud-storages/:connectionUuid/files',
  cloudFiles: (connectionUuid, folderId = 'root') =>
    `/cloud-storages/${connectionUuid}/files${
      folderId !== 'root' ? `?folder=${encodeURIComponent(folderId)}` : ''
    }`,
  CLOUD_CONNECTION_SUCCESS: '/cloud/connections/success',
  CLOUD_CONNECTION_ERROR: '/cloud/connections/error',
  TRANSFER_HISTORY: '/transfer-history',
  TRANSFER_DETAIL: '/transfer-history/:jobUuid',
  transferDetail: (jobUuid) => `/transfer-history/${jobUuid}`,
  ACTIVITY: '/activity',
  PROFILE: '/profile',
  SETTINGS: '/settings',
};

export default PATHS;
