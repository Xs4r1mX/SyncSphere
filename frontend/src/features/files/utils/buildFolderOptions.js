import { ROOT_ID } from '../constants/fileTypes';
import { getProviderRootLabel } from '@/features/cloud/utils/getProviderRootLabel';

export function buildFolderOptions(
  breadcrumbItems,
  listItems,
  excludeItemId = null,
  provider,
) {
  const options = new Map();

  options.set('root', {
    provider_item_id: 'root',
    name: getProviderRootLabel(provider),
  });

  for (const item of breadcrumbItems ?? []) {
    if (item.is_folder && item.provider_item_id !== excludeItemId) {
      options.set(item.provider_item_id, {
        provider_item_id: item.provider_item_id,
        name: item.name,
      });
    }
  }

  for (const item of listItems ?? []) {
    if (
      item.is_folder &&
      !item.trashed &&
      item.provider_item_id !== excludeItemId
    ) {
      options.set(item.provider_item_id, {
        provider_item_id: item.provider_item_id,
        name: item.name,
      });
    }
  }

  return Array.from(options.values());
}
