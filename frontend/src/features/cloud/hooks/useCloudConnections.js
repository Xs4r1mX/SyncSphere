import { useQuery } from '@tanstack/react-query';

import cloudApi from '../api/cloudApi';
import { cloudQueryKeys } from '../constants/queryKeys';

export function useCloudConnections() {
  return useQuery({
    queryKey: cloudQueryKeys.connections(),
    queryFn: () => cloudApi.listConnections(),
  });
}
