export const transferQueryKeys = {
  all: ['transfers'],
  list: (status) => [...transferQueryKeys.all, 'list', status ?? 'all'],
  job: (uuid) => [...transferQueryKeys.all, 'job', uuid],
  items: (uuid) => [...transferQueryKeys.all, 'items', uuid],
};
