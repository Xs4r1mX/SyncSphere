import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import fileApi from '../api/fileApi';
import { fileQueryKeys } from '../constants/queryKeys';

export function useCreateFolder(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ name, parentId }) =>
      fileApi.createFolder(connectionUuid, {
        name,
        parent_id: parentId,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.list(connectionUuid, variables.parentId, false),
      });
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.quota(connectionUuid),
      });
      toast.success('Folder created.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not create folder.');
    },
  });
}
