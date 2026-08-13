import { useInfiniteQuery, useQuery } from '@tanstack/react-query';

import activityApi from '../api/activityApi';
import { activityQueryKeys } from '../constants/queryKeys';

const DEFAULT_LIMIT = 50;

function buildListParams(filters = {}) {
  const params = {
    limit: filters.limit ?? DEFAULT_LIMIT,
    offset: filters.offset ?? 0,
  };

  if (filters.resource_type && filters.resource_type !== 'all') {
    params.resource_type = filters.resource_type;
  }

  if (filters.action) {
    params.action = filters.action;
  }

  if (filters.connection_uuid) {
    params.connection_uuid = filters.connection_uuid;
  }

  if (filters.provider) {
    params.provider = filters.provider;
  }

  return params;
}

export function useActivity(filters = {}) {
  const params = buildListParams(filters);

  return useQuery({
    queryKey: activityQueryKeys.list(params),
    queryFn: () => activityApi.listActivity(params),
  });
}

export function useActivityFeed(filters = {}) {
  const limit = filters.limit ?? DEFAULT_LIMIT;
  const baseFilters = {
    resource_type: filters.resource_type,
    action: filters.action,
    connection_uuid: filters.connection_uuid,
    provider: filters.provider,
    limit,
  };

  return useInfiniteQuery({
    queryKey: activityQueryKeys.list({ ...baseFilters, mode: 'infinite' }),
    queryFn: ({ pageParam = 0 }) =>
      activityApi.listActivity(buildListParams({ ...baseFilters, offset: pageParam })),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => {
      const nextOffset = (lastPage.offset ?? 0) + (lastPage.limit ?? limit);
      if (nextOffset >= (lastPage.total ?? 0)) {
        return undefined;
      }
      return nextOffset;
    },
  });
}
