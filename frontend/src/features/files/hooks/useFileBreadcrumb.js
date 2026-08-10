import { useQuery } from '@tanstack/react-query';

import fileApi from '../api/fileApi';
import { ROOT_ID } from '../constants/fileTypes';
import { fileQueryKeys } from '../constants/queryKeys';

export function useFileBreadcrumb(connectionUuid, folderId, enabled = true) {
  return useQuery({
    queryKey: fileQueryKeys.breadcrumb(connectionUuid, folderId),
    queryFn: () => fileApi.getBreadcrumb(connectionUuid, folderId),
    enabled: Boolean(connectionUuid) && enabled && folderId !== ROOT_ID,
    select: (data) => data.items,
  });
}
