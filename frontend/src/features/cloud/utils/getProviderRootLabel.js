const ROOT_LABELS = {
  google_drive: 'My Drive',
  dropbox: 'All files',
  onedrive: 'OneDrive',
};

export function getProviderRootLabel(provider) {
  return ROOT_LABELS[provider] ?? 'Root';
}

export function getRootBreadcrumbItem(provider) {
  return {
    provider_item_id: 'root',
    name: getProviderRootLabel(provider),
    is_folder: true,
  };
}
