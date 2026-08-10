import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import fileApi from '../api/fileApi';
import { MAX_UPLOAD_BYTES } from '../constants/fileTypes';
import { fileQueryKeys } from '../constants/queryKeys';
import { formatFileSize } from '../utils/formatFileSize';

export function useUploadFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, parentId }) => {
      if (file.size > MAX_UPLOAD_BYTES) {
        throw new Error(
          `File exceeds the maximum allowed size of ${formatFileSize(MAX_UPLOAD_BYTES)}.`,
        );
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('parent_id', parentId);

      return fileApi.uploadFile(connectionUuid, formData);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.list(connectionUuid, variables.parentId, false),
      });
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.quota(connectionUuid),
      });
      toast.success('File uploaded.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not upload file.');
    },
  });
}
