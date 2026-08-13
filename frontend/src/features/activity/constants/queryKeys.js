export const activityQueryKeys = {
  all: ['activity'],
  list: (filters = {}) => [...activityQueryKeys.all, 'list', filters],
};
