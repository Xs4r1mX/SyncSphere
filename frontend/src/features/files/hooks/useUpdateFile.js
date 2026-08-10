import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import fileApi from '../api/fileApi';
import { fileQueryKeys } from '../constants/queryKeys';

function invalidateFileQueries(queryClient, connectionUuid) {
  queryClient.invalidateQueries({ queryKey: fileQueryKeys.all });
  queryClient.invalidateQueries({ queryKey: fileQueryKeys.quota(connectionUuid) });
}

export function useUpdateFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, name, parentId }) => {
      const payload = {};

      if (name !== undefined) {
        payload.name = name;
      }

      if (parentId !== undefined) {
        payload.parent_id = parentId;
      }

      return fileApi.updateItem(connectionUuid, itemId, payload);
    },
    onSuccess: () => {
      invalidateFileQueries(queryClient, connectionUuid);
      toast.success('Item updated.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not update item.');
    },
  });
}
