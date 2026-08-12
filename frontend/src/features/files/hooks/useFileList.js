import { useInfiniteQuery } from '@tanstack/react-query';

import fileApi from '../api/fileApi';
import { fileQueryKeys } from '../constants/queryKeys';

export function useFileList(connectionUuid, { parentId, trashed, enabled = true }) {
  return useInfiniteQuery({
    queryKey: fileQueryKeys.list(connectionUuid, parentId, trashed),
    queryFn: ({ pageParam }) =>
      fileApi.listItems(connectionUuid, {
        parent_id: parentId,
        page_token: pageParam,
        trashed,
      }),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) => lastPage.next_page_token ?? undefined,
    enabled: Boolean(connectionUuid) && enabled,
  });
}
