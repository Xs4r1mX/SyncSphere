import { useQuery } from '@tanstack/react-query';

import fileApi from '../api/fileApi';
import { fileQueryKeys } from '../constants/queryKeys';

export function useFileQuota(connectionUuid) {
  return useQuery({
    queryKey: fileQueryKeys.quota(connectionUuid),
    queryFn: () => fileApi.getQuota(connectionUuid),
    enabled: Boolean(connectionUuid),
  });
}
