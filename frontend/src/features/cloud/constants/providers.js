export const cloudProviders = [
  {
    id: 'google_drive',
    name: 'Google Drive',
    description: 'Connect your Google Drive account to sync files.',
    available: true,
    rootLabel: 'My Drive',
    supportsTrashBrowse: true,
  },
  {
    id: 'dropbox',
    name: 'Dropbox',
    description: 'Sync files from your Dropbox account.',
    available: true,
    rootLabel: 'All files',
    supportsTrashBrowse: true,
  },
  {
    id: 'onedrive',
    name: 'OneDrive',
    description: 'Connect your Microsoft OneDrive account to sync files.',
    available: true,
    rootLabel: 'OneDrive',
    supportsTrashBrowse: false,
  },
];

export function getCloudProvider(providerId) {
  return cloudProviders.find((provider) => provider.id === providerId);
}

export function getAvailableCloudProviders() {
  return cloudProviders.filter((provider) => provider.available);
}

export function providerSupportsTrashBrowse(providerId) {
  return getCloudProvider(providerId)?.supportsTrashBrowse ?? false;
}
