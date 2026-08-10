export function buildFolderOptions(breadcrumbItems, listItems, excludeItemId = null) {
  const options = new Map();

  options.set('root', { provider_item_id: 'root', name: 'My Drive' });

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
