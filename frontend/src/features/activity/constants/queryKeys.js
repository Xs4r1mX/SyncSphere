export const activityQueryKeys = {
  all: ['activity'],
  list: (filters = {}) => [...activityQueryKeys.all, 'list', filters],
  detail: (uuid) => [...activityQueryKeys.all, 'detail', uuid],
};
