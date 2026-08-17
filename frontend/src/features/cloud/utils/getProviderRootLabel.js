import { getCloudProvider } from '../constants/providers';

export function getProviderRootLabel(provider) {
  return getCloudProvider(provider)?.rootLabel ?? 'Root';
}

export function getRootBreadcrumbItem(provider) {
  return {
    provider_item_id: 'root',
    name: getProviderRootLabel(provider),
    is_folder: true,
  };
}

export function getProviderDisplayName(provider) {
  return getCloudProvider(provider)?.name ?? provider?.replaceAll('_', ' ') ?? 'Cloud storage';
}
