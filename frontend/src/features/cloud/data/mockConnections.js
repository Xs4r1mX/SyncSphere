export const mockConnections = [
  {
    id: '1',
    provider: 'Google Drive',
    email: 'user@gmail.com',
    status: 'Connected',
    quotaUsed: 45,
    quotaTotal: 100,
  },
  {
    id: '2',
    provider: 'Dropbox',
    email: 'user@dropbox.com',
    status: 'Connected',
    quotaUsed: 12,
    quotaTotal: 50,
  },
];

export const mockProviders = [
  {
    id: 'google_drive',
    name: 'Google Drive',
    description: 'Connect your Google Drive account to sync files.',
    available: true,
  },
  {
    id: 'dropbox',
    name: 'Dropbox',
    description: 'Sync files from your Dropbox account.',
    available: false,
  },
  {
    id: 'onedrive',
    name: 'OneDrive',
    description: 'Connect Microsoft OneDrive for file transfers.',
    available: false,
  },
];
