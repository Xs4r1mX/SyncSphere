export const fileQueryKeys = {
  all: ['files'],
  list: (connectionUuid, parentId, trashed) => [
    ...fileQueryKeys.all,
    'list',
    connectionUuid,
    parentId,
    trashed,
  ],
  breadcrumb: (connectionUuid, itemId) => [
    ...fileQueryKeys.all,
    'breadcrumb',
    connectionUuid,
    itemId,
  ],
  quota: (connectionUuid) => [...fileQueryKeys.all, 'quota', connectionUuid],
};
